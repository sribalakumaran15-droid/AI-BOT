import { useState } from 'react'
import { Menu, Search, Bell } from 'lucide-react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
export default function AppLayout() { const [open,setOpen]=useState(false); return <div className="app-shell"><Sidebar open={open} onClose={()=>setOpen(false)}/><main className="main"><header className="topbar"><button className="menu-button" onClick={()=>setOpen(true)}><Menu size={20}/></button><div className="top-search"><Search size={17}/><input placeholder="Search your workspace..."/></div><div className="top-actions"><button><Bell size={19}/></button><div className="avatar">SA</div></div></header><section className="content"><Outlet/></section></main></div> }
