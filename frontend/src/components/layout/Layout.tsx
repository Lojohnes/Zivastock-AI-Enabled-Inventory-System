import React from 'react'
import { Outlet } from 'react-router-dom'
import { Box, AppBar, Toolbar, Typography, IconButton } from '@mui/material'
import { Menu as MenuIcon } from '@mui/icons-material'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

export const Layout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false)
  const sidebarWidth = sidebarCollapsed ? 72 : 240

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { xs: '100%', sm: `calc(100% - ${sidebarWidth}px)` },
          ml: { sm: `${sidebarWidth}px` },
          transition: 'width 180ms ease, margin 180ms ease',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Box component="img" src="/zivastock-mark.svg" alt="" aria-hidden="true" sx={{ width: 34, height: 34, mr: 1 }} />
          <Typography variant="h6" noWrap component="div">
            ZivaStock
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
          <Header />
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: sidebarWidth }, flexShrink: { sm: 0 }, transition: 'width 180ms ease' }}
      >
        <Sidebar mobileOpen={mobileOpen} collapsed={sidebarCollapsed} onDrawerToggle={handleDrawerToggle} onCollapseToggle={() => setSidebarCollapsed((value) => !value)} />
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 1.5, sm: 2.5, lg: 3 },
          width: { xs: '100%', sm: `calc(100% - ${sidebarWidth}px)` },
          minWidth: 0,
          transition: 'width 180ms ease',
          mt: { xs: '56px', sm: '64px' },
          overflowX: 'hidden',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  )
}
