import { FileQuestion } from 'lucide-react'
export default function EmptyState({ title, text, action }) { return <div className="empty-state"><FileQuestion size={32}/><h3>{title}</h3><p>{text}</p>{action}</div> }
