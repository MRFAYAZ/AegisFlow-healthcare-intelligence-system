import type { Role } from '../types'

export type AppRoute =
  | '/dashboard'
  | '/emergency'
  | '/inventory'
  | '/shortage'
  | '/transfers'
  | '/dispatcher'
  | '/analytics'
  | '/map'
  | '/shop'
  | '/procurement'

export interface WorkspaceDefinition {
  name: string
  description: string
  landingRoute: AppRoute
  sections: { name: string; routes: AppRoute[] }[]
}

export const routePermissions: Record<AppRoute, Role[]> = {
  '/dashboard': ['system_admin', 'hospital_admin', 'pharmacist', 'shop_owner', 'emergency_operator', 'dispatcher', 'supplier_manager'],
  '/emergency': ['system_admin', 'hospital_admin', 'emergency_operator', 'dispatcher'],
  '/inventory': ['system_admin', 'hospital_admin', 'pharmacist', 'shop_owner', 'supplier_manager'],
  '/shortage': ['system_admin', 'hospital_admin', 'pharmacist', 'emergency_operator', 'supplier_manager'],
  '/transfers': ['system_admin', 'hospital_admin', 'emergency_operator', 'dispatcher', 'supplier_manager'],
  '/dispatcher': ['system_admin', 'emergency_operator', 'dispatcher'],
  '/analytics': ['system_admin', 'hospital_admin', 'emergency_operator', 'supplier_manager'],
  '/map': ['system_admin', 'hospital_admin', 'emergency_operator', 'dispatcher', 'supplier_manager'],
  '/shop': ['system_admin', 'pharmacist', 'shop_owner'],
  '/procurement': ['system_admin', 'hospital_admin', 'emergency_operator', 'supplier_manager'],
}

export function normalizeRole(role?: string | null): Role | null {
  if (!role) return null

  const normalized = role.toLowerCase()
  return (normalized === 'supplier' ? 'supplier_manager' : normalized) as Role
}

export function canAccessRoute(role: string | null | undefined, route: AppRoute): boolean {
  const normalizedRole = normalizeRole(role)
  return normalizedRole !== null && routePermissions[route].includes(normalizedRole)
}

const workspaceDefinitions: Record<Role, WorkspaceDefinition> = {
  system_admin: {
    name: 'Governance workspace',
    description: 'Platform oversight and network visibility',
    landingRoute: '/dashboard',
    sections: [
      { name: 'Command', routes: ['/dashboard', '/analytics', '/map'] },
      { name: 'Operations', routes: ['/emergency', '/shortage', '/procurement', '/transfers', '/dispatcher'] },
    ],
  },
  hospital_admin: {
    name: 'Hospital operations',
    description: 'Emergency decisions, inventory and incoming transfers',
    landingRoute: '/dashboard',
    sections: [
      { name: 'Hospital', routes: ['/dashboard', '/emergency', '/inventory', '/shortage', '/procurement', '/transfers'] },
      { name: 'Intelligence', routes: ['/analytics', '/map'] },
    ],
  },
  emergency_operator: {
    name: 'Emergency operations center',
    description: 'Coordinate shortages, allocation and response logistics',
    landingRoute: '/emergency',
    sections: [
      { name: 'Operations', routes: ['/emergency', '/shortage', '/procurement', '/transfers', '/dispatcher'] },
      { name: 'Situation awareness', routes: ['/dashboard', '/map', '/analytics'] },
    ],
  },
  dispatcher: {
    name: 'Logistics control tower',
    description: 'Assign, dispatch and close active healthcare transfers',
    landingRoute: '/dispatcher',
    sections: [
      { name: 'Logistics', routes: ['/dispatcher', '/transfers'] },
      { name: 'Situation awareness', routes: ['/dashboard', '/map'] },
    ],
  },
  pharmacist: {
    name: 'Donor operations',
    description: 'Manage safe inventory and transfer requests',
    landingRoute: '/inventory',
    sections: [
      { name: 'Donor facility', routes: ['/inventory', '/shortage', '/transfers', '/shop'] },
      { name: 'Overview', routes: ['/dashboard'] },
    ],
  },
  shop_owner: {
    name: 'Donor operations',
    description: 'Manage shop inventory and supply requests',
    landingRoute: '/inventory',
    sections: [
      { name: 'Donor facility', routes: ['/inventory', '/transfers', '/shop'] },
      { name: 'Overview', routes: ['/dashboard'] },
    ],
  },
  supplier_manager: {
    name: 'Supply operations',
    description: 'Monitor supply inventory and network demand',
    landingRoute: '/inventory',
    sections: [
      { name: 'Supply', routes: ['/inventory', '/shortage', '/procurement', '/transfers'] },
      { name: 'Intelligence', routes: ['/dashboard', '/analytics', '/map'] },
    ],
  },
}

export function getWorkspace(role?: string | null): WorkspaceDefinition | null {
  const normalizedRole = normalizeRole(role)
  return normalizedRole ? workspaceDefinitions[normalizedRole] : null
}