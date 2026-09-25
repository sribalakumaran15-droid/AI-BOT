import { createContext, useContext, useState } from 'react'
import { apiCall, api } from '../services/api'

const AuthContext = createContext(null)
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem('studyai_user') || 'null'))
  const [loading, setLoading] = useState(false)
  const save = (data) => { localStorage.setItem('studyai_token', data.token); localStorage.setItem('studyai_user', JSON.stringify(data.user)); setUser(data.user) }
  const login = async (values) => { setLoading(true); try { save(await apiCall(api.post('/auth/login', values))) } finally { setLoading(false) } }
  const register = async (values) => { setLoading(true); try { save(await apiCall(api.post('/auth/register', values))) } finally { setLoading(false) } }
  const logout = () => { localStorage.removeItem('studyai_token'); localStorage.removeItem('studyai_user'); setUser(null) }
  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
}
export const useAuth = () => useContext(AuthContext)
