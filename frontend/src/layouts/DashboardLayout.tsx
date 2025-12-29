import { ActionIcon, Anchor, Avatar, Breadcrumbs } from '@mantine/core'
import React from 'react'
import { IconBell, IconHistory } from '@tabler/icons-react'
import styles from './Dashboard.module.css'
import MenuItem from '@/components/MenuItem'
import { menuItems } from '@/app-util/menu'

type Props = {
  children: React.ReactNode
  projectName?: string
}

const items = [
  { title: 'Dashboard', href: '#' },
  { title: 'name', href: '#' },
  { title: 'home', href: '#' },
].map((item, index) => (
  <Anchor href={item.href} key={index}>
    {item.title}
  </Anchor>
))

export const DashboardLayout = ({ children, projectName = 'Scroller title' }: Props) => {
  return (
    <div className={styles.root}>
      <aside className={styles.sidebar}>
        <div className={styles.sidebarInner}>
          <div className={styles.brand}>
            <Avatar color="blue" radius="xl" size={36} />
            <div className={styles.brandText}>
              <p className={styles.projectName}>{projectName}</p>
            </div>
          </div>

          <nav className={styles.menu}>
            {menuItems.map((item) => (
              <MenuItem key={item.title} label={item.title} href={item.href} icon={item.icon} />
            ))}
          </nav>
        </div>
      </aside>

      <div className={styles.contentWrap}>
        <header className={styles.header}>
          <Breadcrumbs>{items}</Breadcrumbs>
          <div className={styles.headerIcons}>
            <ActionIcon variant="transparent">
              <IconHistory size={14} />
            </ActionIcon>
            <ActionIcon variant="transparent">
              <IconBell size={14} />
            </ActionIcon>
          </div>
        </header>

        <main className={styles.main}>{children}</main>
      </div>
    </div>
  )
}

export default DashboardLayout
