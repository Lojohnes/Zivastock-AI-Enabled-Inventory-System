from datetime import date, datetime, timedelta, timezone
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.forecast import ForecastResult, InventoryExposure


class ForecastingService:
    """Compare reproducible demand baselines and derive inventory exposure."""

    MODELS = ("naive", "moving_average", "exponential_smoothing")

    def __init__(self, db: Optional[Session] = None, calculation_version: str = "v1"):
        self.db = db
        self.calculation_version = calculation_version

    def compare_models(
        self,
        sales: pd.DataFrame,
        as_of_date: date,
        validation_horizon: int = 7,
        moving_average_window: int = 7,
    ) -> pd.DataFrame:
        series_map = self._sales_series(sales, as_of_date)
        rows = []
        for key, series in series_map.items():
            for model in self.MODELS:
                metrics = self._evaluate(series, model, validation_horizon, moving_average_window)
                rows.append({
                    "product_id": key[0],
                    "location_id": key[1],
                    "model_algorithm": model,
                    **metrics,
                })
        return pd.DataFrame(rows)

    def forecast(
        self,
        sales: pd.DataFrame,
        as_of_date: date,
        horizon_days: int = 7,
        model: Optional[str] = None,
        validation_horizon: int = 7,
        moving_average_window: int = 7,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        if horizon_days < 1:
            raise ValueError("horizon_days must be greater than zero")
        series_map = self._sales_series(sales, as_of_date)
        comparison = self.compare_models(sales, as_of_date, validation_horizon, moving_average_window)
        forecast_rows = []
        selected_models = {}
        for key, series in series_map.items():
            selected = model or self._select_model(comparison, key)
            if selected not in self.MODELS:
                raise ValueError(f"Unsupported forecast model: {selected}")
            selected_models[key] = selected
            prediction = self._predict(series, selected, horizon_days, moving_average_window)
            uncertainty = self._uncertainty(series, selected, moving_average_window)
            for offset, predicted in enumerate(prediction, start=1):
                forecast_rows.append({
                    "product_id": key[0],
                    "location_id": self._optional_int(key[1]),
                    "model_algorithm": selected,
                    "forecast_date": as_of_date + timedelta(days=offset),
                    "horizon_days": horizon_days,
                    "predicted_demand": max(0.0, float(predicted)),
                    "lower_bound": max(0.0, float(predicted) - 1.96 * uncertainty),
                    "upper_bound": max(0.0, float(predicted) + 1.96 * uncertainty),
                    "evaluation_metrics": self._metrics_for(comparison, key, selected),
                })
        return pd.DataFrame(forecast_rows), comparison

    def exposure(
        self,
        forecasts: pd.DataFrame,
        inventory: pd.DataFrame,
        calculation_date: date,
        safety_stock: float | pd.Series = 0,
        target_days: int = 14,
        slow_moving_days: int = 30,
    ) -> pd.DataFrame:
        required_forecast = {"product_id", "predicted_demand"}
        required_inventory = {"product_id", "current_quantity"}
        if not required_forecast.issubset(forecasts.columns):
            raise ValueError("Forecasts require product_id and predicted_demand")
        if not required_inventory.issubset(inventory.columns):
            raise ValueError("Inventory requires product_id and current_quantity")

        group_keys = ["product_id"]
        use_location = (
            "location_id" in forecasts.columns
            and "location_id" in inventory.columns
            and (forecasts["location_id"].notna().any() or inventory["location_id"].notna().any())
        )
        if use_location:
            group_keys.append("location_id")
            forecasts = forecasts.copy()
            inventory = inventory.copy()
            forecasts["location_id"] = forecasts["location_id"].fillna("__NONE__").astype(str)
            inventory["location_id"] = inventory["location_id"].fillna("__NONE__").astype(str)
        demand = forecasts.groupby(group_keys, dropna=False)["predicted_demand"].mean().reset_index(name="predicted_daily_demand")
        merged = inventory.merge(demand, on=group_keys, how="left")
        if use_location:
            merged["location_id"] = merged["location_id"].replace("__NONE__", None)
        merged["predicted_daily_demand"] = pd.to_numeric(merged["predicted_daily_demand"], errors="coerce").fillna(0)
        merged["current_quantity"] = pd.to_numeric(merged["current_quantity"], errors="coerce").fillna(0).clip(lower=0)
        if isinstance(safety_stock, pd.Series):
            merged["safety_stock"] = safety_stock.reindex(merged.index).fillna(0).astype(float)
        else:
            merged["safety_stock"] = float(safety_stock)

        rows = []
        for _, row in merged.iterrows():
            current = float(row["current_quantity"])
            daily = float(row["predicted_daily_demand"])
            safe = float(row["safety_stock"])
            available = max(0.0, current - safe)
            days = available / daily if daily > 0 else None
            stockout_date = calculation_date + timedelta(days=max(0, int(days))) if days is not None else None
            risk = self._stockout_risk(days)
            excess = max(0.0, current - (daily * target_days + safe)) if daily > 0 else current
            non_moving = int(daily == 0)
            slow_moving = int(not non_moving and days is not None and days >= slow_moving_days)
            explanation = []
            if risk in {"HIGH", "CRITICAL"}:
                explanation.append(f"Available stock covers approximately {days:.1f} days of predicted demand")
            if non_moving:
                explanation.append("No predicted demand in the forecast horizon")
            elif slow_moving:
                explanation.append(f"Inventory cover exceeds the {slow_moving_days}-day slow-moving threshold")
            if excess > 0:
                explanation.append(f"Approximately {excess:.1f} units exceed the {target_days}-day target stock")
            rows.append({
                "product_id": int(row["product_id"]),
                "location_id": self._optional_int(row.get("location_id")),
                "calculation_date": calculation_date,
                "forecast_model": str(row.get("model_algorithm", "selected")),
                "current_quantity": current,
                "predicted_daily_demand": daily,
                "safety_stock": safe,
                "days_until_stockout": days,
                "stockout_date": stockout_date,
                "stockout_risk": risk,
                "excess_quantity": excess,
                "slow_moving": slow_moving,
                "non_moving": non_moving,
                "explanation": explanation,
                "calculation_version": self.calculation_version,
            })
        return pd.DataFrame(rows)

    def scenario_analysis(
        self,
        current_quantity: float,
        predicted_daily_demand: float,
        safety_stock: float = 0,
        horizon_days: int = 7,
        demand_change_pct: float = 0,
        supplier_delay_days: int = 0,
    ) -> dict:
        if current_quantity < 0 or predicted_daily_demand < 0:
            raise ValueError("Inventory and demand cannot be negative")
        if horizon_days < 1 or supplier_delay_days < 0:
            raise ValueError("Scenario horizon must be positive and delay cannot be negative")
        adjusted_daily = predicted_daily_demand * (1 + demand_change_pct / 100)
        demand_during_delay = adjusted_daily * supplier_delay_days
        available = max(0.0, current_quantity - safety_stock - demand_during_delay)
        days_until_stockout = available / adjusted_daily if adjusted_daily > 0 else None
        ending_quantity = max(0.0, available - adjusted_daily * horizon_days)
        return {
            "current_quantity": current_quantity,
            "adjusted_daily_demand": adjusted_daily,
            "demand_change_pct": demand_change_pct,
            "supplier_delay_days": supplier_delay_days,
            "safety_stock": safety_stock,
            "days_until_stockout": days_until_stockout,
            "ending_quantity_after_horizon": ending_quantity,
            "stockout_risk": self._stockout_risk(days_until_stockout),
        }

    def persist_forecasts(self, forecasts: pd.DataFrame, model_version_id: Optional[int] = None) -> int:
        if not self.db:
            raise ValueError("A database session is required")
        for row in forecasts.to_dict("records"):
            self.db.add(ForecastResult(
                product_id=int(row["product_id"]),
                location_id=self._optional_int(row.get("location_id")),
                model_version_id=model_version_id,
                model_algorithm=row["model_algorithm"],
                forecast_date=self._date_value(row["forecast_date"]),
                horizon_days=int(row["horizon_days"]),
                predicted_demand=float(row["predicted_demand"]),
                lower_bound=float(row["lower_bound"]),
                upper_bound=float(row["upper_bound"]),
                evaluation_metrics=row.get("evaluation_metrics", {}),
            ))
        self.db.commit()
        return len(forecasts)

    def persist_exposure(self, exposure: pd.DataFrame) -> int:
        if not self.db:
            raise ValueError("A database session is required")
        for row in exposure.to_dict("records"):
            self.db.add(InventoryExposure(
                product_id=int(row["product_id"]),
                location_id=self._optional_int(row.get("location_id")),
                calculation_date=self._date_value(row["calculation_date"]),
                forecast_model=row["forecast_model"],
                current_quantity=float(row["current_quantity"]),
                predicted_daily_demand=float(row["predicted_daily_demand"]),
                safety_stock=float(row["safety_stock"]),
                days_until_stockout=row.get("days_until_stockout"),
                stockout_date=self._date_value(row["stockout_date"]) if row.get("stockout_date") is not None else None,
                stockout_risk=row["stockout_risk"],
                excess_quantity=float(row["excess_quantity"]),
                slow_moving=int(row["slow_moving"]),
                non_moving=int(row["non_moving"]),
                explanation=row["explanation"],
                calculation_version=row["calculation_version"],
            ))
        self.db.commit()
        return len(exposure)

    def _sales_series(self, sales: pd.DataFrame, as_of_date: date) -> dict:
        required = {"product_id", "event_type", "quantity", "event_timestamp"}
        if not required.issubset(sales.columns):
            raise ValueError(f"Sales data requires: {', '.join(sorted(required))}")
        frame = sales.copy()
        frame["event_timestamp"] = pd.to_datetime(frame["event_timestamp"], utc=True, errors="coerce")
        frame = frame[(frame["event_type"].astype(str).str.upper() == "SALE") & frame["event_timestamp"].notna()]
        frame = frame[frame["event_timestamp"].dt.date <= as_of_date]
        if frame.empty:
            return {}
        frame["event_date"] = frame["event_timestamp"].dt.date
        frame["quantity"] = pd.to_numeric(frame["quantity"], errors="coerce").fillna(0).clip(lower=0)
        if "location_id" not in frame:
            frame["location_id"] = None
        result = {}
        for key, group in frame.groupby(["product_id", "location_id"], dropna=False):
            start = group["event_date"].min()
            dates = pd.date_range(start, as_of_date, freq="D").date
            result[key] = group.groupby("event_date")["quantity"].sum().reindex(dates, fill_value=0).astype(float)
        return result

    def _evaluate(self, series: pd.Series, model: str, horizon: int, window: int) -> dict:
        if len(series) <= horizon:
            return {"mae": None, "rmse": None, "wape": None, "validation_records": 0}
        train, actual = series.iloc[:-horizon], series.iloc[-horizon:]
        predicted = self._predict(train, model, horizon, window)
        errors = actual.to_numpy() - predicted
        return {
            "mae": float(abs(errors).mean()),
            "rmse": float((errors ** 2).mean() ** 0.5),
            "wape": float(abs(errors).sum() / max(actual.sum(), 1) * 100),
            "validation_records": horizon,
        }

    def _predict(self, series: pd.Series, model: str, horizon: int, window: int) -> list[float]:
        if series.empty:
            return [0.0] * horizon
        if model == "naive":
            value = float(series.iloc[-1])
        elif model == "moving_average":
            value = float(series.tail(window).mean())
        elif model == "exponential_smoothing":
            value = float(series.ewm(alpha=0.3, adjust=False).mean().iloc[-1])
        else:
            raise ValueError(f"Unsupported forecast model: {model}")
        return [max(0.0, value)] * horizon

    def _uncertainty(self, series: pd.Series, model: str, window: int) -> float:
        if len(series) < 2:
            return 0.0
        fitted = pd.Series(self._predict(series.iloc[:-1], model, 1, window), index=[series.index[-1]])
        residuals = series.iloc[1:] - series.iloc[:-1].to_numpy()
        return float(residuals.std(ddof=0)) if len(residuals) else float(fitted.std(ddof=0))

    @staticmethod
    def _select_model(comparison: pd.DataFrame, key: tuple) -> str:
        rows = comparison[(comparison["product_id"] == key[0]) & (comparison["location_id"].isna() if pd.isna(key[1]) else comparison["location_id"] == key[1])]
        if rows.empty:
            return "moving_average"
        rows = rows.copy()
        rows["sort_wape"] = rows["wape"].fillna(float("inf"))
        return str(rows.sort_values(["sort_wape", "mae"], na_position="last").iloc[0]["model_algorithm"])

    @staticmethod
    def _metrics_for(comparison: pd.DataFrame, key: tuple, model: str) -> dict:
        rows = comparison[(comparison["product_id"] == key[0]) & (comparison["model_algorithm"] == model)]
        return rows.iloc[0].drop(labels=["product_id", "location_id", "model_algorithm"]).dropna().to_dict() if not rows.empty else {}

    @staticmethod
    def _stockout_risk(days: Optional[float]) -> str:
        if days is None:
            return "LOW"
        if days <= 2:
            return "CRITICAL"
        if days <= 5:
            return "HIGH"
        if days <= 10:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _optional_int(value):
        return None if value is None or pd.isna(value) else int(value)

    @staticmethod
    def _date_value(value):
        return value if isinstance(value, date) else pd.Timestamp(value).date()
