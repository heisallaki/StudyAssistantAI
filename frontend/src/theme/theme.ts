import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2454FF',
    },
    secondary: {
      main: '#00B894',
    },
    background: {
      default: '#F5F7FB',
    },
  },
  typography: {
    fontFamily: ['Inter', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'].join(','),
  },
  shape: {
    borderRadius: 10,
  },
})

export default theme