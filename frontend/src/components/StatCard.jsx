import { ArrowUpRight } from 'lucide-react'
export default function StatCard({ icon:Icon, label, value, note, tone='cyan' }) { return <div className="stat-card"><div className={`stat-icon ${tone}`}><Icon size={19}/></div><div className="stat-copy"><span>{label}</span><strong>{value}</strong><small><ArrowUpRight size={13}/>{note}</small></div></div> }
