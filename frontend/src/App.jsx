import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { Header } from './components/Navbar'
import { Home } from './pages/Home'
import { ProductDetail } from './pages/ProductDetail'
import { Cart } from './pages/Cart'
import { Checkout } from './pages/Checkout'
import { Account } from './pages/Account'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Likes } from './pages/Likes'

import Woman from './pages/Woman'
import Men from './pages/Men'
import Kids from './pages/Kids'
import New from './pages/New'
import Offers from './pages/Offers'

import { CartProvider } from './context/CartContext'
import { LikesProvider } from './context/LikesContext'
import { Notification } from './components/Notification'
import { LikeNotification } from './components/LikeNotification'

function AppContent() {
  const location = useLocation()
  const isAuthPage = ['/login', '/register'].includes(location.pathname)

  return (
    <div className="min-h-screen bg-white dark:bg-zinc-900 transition-colors duration-300">
      {!isAuthPage && <Header />}
      {!isAuthPage && <Notification />}
      {!isAuthPage && <LikeNotification />}

      <main className={`bg-white dark:bg-zinc-900 transition-colors duration-300 ${isAuthPage ? 'h-screen' : ''}`}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/producto/:id" element={<ProductDetail />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/cuenta" element={<Account />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/favoritos" element={<Likes />} />

          {/* 🔥 Nuevas rutas funcionales */}
          <Route path="/woman" element={<Woman />} />
          <Route path="/men" element={<Men />} />
          <Route path="/kids" element={<Kids />} />
          <Route path="/new" element={<New />} />
          <Route path="/offers" element={<Offers />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <CartProvider>
      <LikesProvider>
        <Router>
          <AppContent />
        </Router>
      </LikesProvider>
    </CartProvider>
  )
}

export default App
