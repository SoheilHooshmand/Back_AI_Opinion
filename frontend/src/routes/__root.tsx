import { Outlet, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools'
import { TanStackDevtools } from '@tanstack/react-devtools'
import { MantineProvider } from '@mantine/core'

import '@mantine/core/styles.css'

// ‼️ import dropzone styles after core package styles
import '@mantine/dropzone/styles.css'
// ‼️ import notifications styles after core package styles
import '@mantine/notifications/styles.css'

import { Notifications } from '@mantine/notifications'
import theme from '@/app-util/theme'

export const Route = createRootRoute({
  component: () => (
    <>
      <MantineProvider theme={theme} defaultColorScheme="light">
        <Notifications />
        <Outlet />
      </MantineProvider>
      <TanStackDevtools
        config={{
          position: 'bottom-right',
        }}
        plugins={[
          {
            name: 'Tanstack Router',
            render: <TanStackRouterDevtoolsPanel />,
          },
        ]}
      />
    </>
  ),
})
