import { Link } from '@tanstack/react-router'
import React from 'react'
import styles from './menuItem.module.css'

type Props = {
  icon: React.ReactNode
  label: string
  href: string
  active?: boolean
}
const MenuItem = ({ href, icon, label, active }: Props) => {
  return (
    <Link to={href} className={`${styles.menuItem} ${active ? styles.menuItemActive : ''}`}>
      <span className={styles.menuIcon}>{icon}</span>
      <span className={styles.menuLabel}>{label}</span>
    </Link>
  )
}

export default MenuItem
