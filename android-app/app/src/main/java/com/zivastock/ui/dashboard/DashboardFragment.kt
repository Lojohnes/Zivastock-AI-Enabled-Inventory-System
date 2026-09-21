package com.zivastock.ui.dashboard

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.zivastock.R
import com.zivastock.databinding.FragmentDashboardBinding
import dagger.hilt.android.AndroidEntryPoint
import java.text.DecimalFormat

@AndroidEntryPoint
class DashboardFragment : Fragment() {

    private var _binding: FragmentDashboardBinding? = null
    private val binding get() = _binding!!
    private val viewModel: DashboardViewModel by viewModels()
    private val decimalFormat = DecimalFormat("0.##")

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.activeSession.observe(viewLifecycleOwner) { session ->
            viewModel.loadDetails(session)
        }

        viewModel.details.observe(viewLifecycleOwner) { details ->
            if (details == null) {
                binding.cardActiveSession.visibility = View.GONE
                binding.tvNoActiveSession.visibility = View.VISIBLE
                return@observe
            }

            binding.cardActiveSession.visibility = View.VISIBLE
            binding.tvNoActiveSession.visibility = View.GONE

            binding.tvSessionName.text = details.name
            binding.tvSessionStatus.text = getString(R.string.session_status, details.status)
            binding.tvSessionLocation.text = details.locationName
            binding.tvSessionType.text = details.sessionType
            binding.tvShelves.text = details.shelves.joinToString("\n")
        }

        viewModel.dashboardStats.observe(viewLifecycleOwner) { stats ->
            binding.tvPendingSync.text = stats.pendingSyncCount.toString()
            binding.tvCompletedShelves.text = stats.completedShelves.toString()
            binding.tvCompletedShelvesSubtitle.text = getString(
                R.string.dashboard_subtitle_of,
                stats.completedShelves,
                stats.totalShelves
            )
            binding.tvCompletedSections.text = stats.completedSections.toString()
            binding.tvCompletedSectionsSubtitle.text = getString(
                R.string.dashboard_subtitle_of,
                stats.completedSections,
                stats.totalSections
            )
            binding.tvProductsCounted.text = stats.productsCounted.toString()
            binding.tvProductsCountedSubtitle.text = getString(
                R.string.dashboard_subtitle_percentage,
                stats.countedProductsPercentage
            )
            binding.tvProductsRemaining.text = stats.productsRemaining.toString()
            binding.tvVariances.text = stats.varianceCount.toString()
            binding.tvVariancesSubtitle.text = getString(
                R.string.dashboard_subtitle_variance_total,
                decimalFormat.format(stats.totalVariance)
            )
            binding.tvAiReadiness.text = if (stats.pendingSyncCount > 0) {
                "${stats.pendingSyncCount} local change(s) waiting to sync. Sync before reviewing AI risk and forecast results."
            } else {
                "Counts are synchronised. Central AI anomaly, risk and forecast analysis is ready when the server pipeline has processed the data."
            }
        }

        viewModel.chartData.observe(viewLifecycleOwner) { data ->
            binding.barChart.setData(data)
        }

        viewModel.syncState.observe(viewLifecycleOwner) { state ->
            when (state) {
                is DashboardViewModel.SyncState.Loading -> binding.progressBar.visibility = View.VISIBLE
                else -> binding.progressBar.visibility = View.GONE
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
