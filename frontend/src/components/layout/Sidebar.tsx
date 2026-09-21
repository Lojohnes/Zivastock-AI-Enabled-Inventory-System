import React from 'react'
import { Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Toolbar, Divider } from '@mui/material'
import { Dashboard, Inventory, Assignment, Report, People, Security, Logout, CloudUpload, AutoAwesome, Science, PointOfSale } from '@mui/icons-material'
import { useNavigate, useLocation } from 'react-router-dom'

interface SidebarProps {
  mobileOpen: boolean
  onDrawerToggle: () => void
}

const drawerWidth = 240

export const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, onDrawerToggle }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
    { text: 'AI Command Centre', icon: <AutoAwesome />, path: '/command-centre' },
    { text: 'AI Model Laboratory', icon: <Science />, path: '/model-laboratory' },
    { text: 'Demo POS', icon: <PointOfSale />, path: '/demo-pos' },
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
      <Box sx={{ px: 2, py: 2, display: 'flex', justifyContent: 'center' }}>
        <Box component="img" src="/zivastock-logo.svg" alt="ZivaStock" sx={{ width: '100%', maxWidth: 205, height: 112, objectFit: 'contain' }} />
      </Box>
      <Toolbar />
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path)
                if (mobileOpen) onDrawerToggle()
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={handleLogout}>
            <ListItemIcon>
              <Logout />
            </ListItemIcon>
            <ListItemText primary="Logout" />
          </ListItemButton>
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
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
        open
      >
        {drawer}
      </Drawer>
    </>
  )
}
