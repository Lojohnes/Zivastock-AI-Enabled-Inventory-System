import React from 'react'
import { Box, Drawer, IconButton, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Toolbar, Divider, Tooltip } from '@mui/material'
import { Dashboard, Inventory, Assignment, Report, People, Security, Logout, CloudUpload, AutoAwesome, Science, PointOfSale, ManageSearch, ChevronLeft, ChevronRight } from '@mui/icons-material'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAppSelector } from '../../hooks/redux'

interface SidebarProps {
  mobileOpen: boolean
  collapsed: boolean
  onDrawerToggle: () => void
  onCollapseToggle: () => void
}

const drawerWidth = 240
const collapsedWidth = 72

export const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, collapsed, onDrawerToggle, onCollapseToggle }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const user = useAppSelector((state) => state.auth.user)
  const canViewAudit = user?.permissions?.includes('reports.view_audit')

  const menuItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
    { text: 'AI Command Centre', icon: <AutoAwesome />, path: '/command-centre' },
    { text: 'AI Model Laboratory', icon: <Science />, path: '/model-laboratory' },
    { text: 'Demo POS', icon: <PointOfSale />, path: '/demo-pos' },
    ...(canViewAudit ? [{ text: 'Audit Trail', icon: <ManageSearch />, path: '/audit' }] : []),
    { text: 'Stocktake', icon: <Inventory />, path: '/stocktake' },
    { text: 'Products', icon: <Assignment />, path: '/products' },
    { text: 'Import Inventory', icon: <CloudUpload />, path: '/import' },
    { text: 'Reports', icon: <Report />, path: '/reports' },
    { text: 'Counts', icon: <Assignment />, path: '/counts' },
    { text: 'Users', icon: <People />, path: '/users' },
    { text: 'Roles & Permissions', icon: <Security />, path: '/roles' },
  ]

  const handleLogout = () => {
    localStorage.clear()
    navigate('/login')
  }

  const drawer = (
    <div>
      <Box sx={{ px: collapsed ? 1 : 2, py: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 1 }}>
        <Box component="img" src={collapsed ? '/zivastock-mark.svg' : '/zivastock-logo.svg'} alt="ZivaStock" sx={{ width: collapsed ? 42 : '100%', maxWidth: collapsed ? 42 : 205, height: collapsed ? 42 : 112, objectFit: 'contain' }} />
        <IconButton onClick={onCollapseToggle} aria-label={collapsed ? 'Expand menu' : 'Collapse menu'} sx={{ display: { xs: 'none', sm: 'inline-flex' } }}>
          {collapsed ? <ChevronRight /> : <ChevronLeft />}
        </IconButton>
      </Box>
      <Toolbar />
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <Tooltip title={collapsed ? item.text : ''} placement="right">
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => {
                  navigate(item.path)
                  if (mobileOpen) onDrawerToggle()
                }}
                sx={{ justifyContent: collapsed ? 'center' : 'initial', px: collapsed ? 1.5 : 2 }}
              >
                <ListItemIcon sx={{ minWidth: collapsed ? 0 : 40, justifyContent: 'center' }}>{item.icon}</ListItemIcon>
                {!collapsed && <ListItemText primary={item.text} />}
              </ListItemButton>
            </Tooltip>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem disablePadding>
          <Tooltip title={collapsed ? 'Logout' : ''} placement="right">
            <ListItemButton onClick={handleLogout} sx={{ justifyContent: collapsed ? 'center' : 'initial', px: collapsed ? 1.5 : 2 }}>
              <ListItemIcon sx={{ minWidth: collapsed ? 0 : 40, justifyContent: 'center' }}><Logout /></ListItemIcon>
              {!collapsed && <ListItemText primary="Logout" />}
            </ListItemButton>
          </Tooltip>
        </ListItem>
      </List>
    </div>
  )

  return (
    <>
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
      >
        {drawer}
      </Drawer>
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: collapsed ? collapsedWidth : drawerWidth, transition: 'width 180ms ease' },
        }}
        open
      >
        {drawer}
      </Drawer>
    </>
  )
}
