
import { createBrowserRouter, RouterProvider } from 'react-router'
import './App.css'
import MainPage from '../pages/MainPage/MainPage'
import RootLayout from '../pages/layouts/RootLayout'


function App() {

  const router = createBrowserRouter([
    {
      element: <RootLayout/>,
      children: [
        {
          path:'/',
          element:<MainPage/>
        },
       
      ]
    },
    
  ])

  return (
    <RouterProvider router={router}/>
  )


}

export default App
