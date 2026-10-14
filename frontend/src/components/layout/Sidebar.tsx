import { NavLink, useNavigate } from "react-router-dom"
import { useEmergencies } from "../../hooks/useEmergency"
import { useCurrentUser } from "../../hooks/useCurrentUser"

type NavItem = { to: string; icon: string; label: string; badgeType?: "red" | "orange" }

const networkItems: NavItem[] = [
  { to: "/dashboard", icon: "⊞", label: "Dashboard" },
  { to: "/emergency", icon: "⚠", label: "Emergency ops", badgeType: "red" },
  { to: "/inventory", icon: "▦", label: "Inventory" },
  { to: "/shortage", icon: "◉", label: "Shortage intelligence", badgeType: "orange" },
  { to: "/transfers", icon: "⇅", label: "Transfer control" },
  { to: "/analytics", icon: "▤", label: "Analytics" },
  { to: "/map", icon: "⊙", label: "Facility network" },
]

const sectionsByRole: Record<string, Array<{ section: string; items: NavItem[] }>> = {
  system_admin: [
    { section: "Operations", items: networkItems },
    { section: "Facility operations", items: [{ to: "/shop", icon: "⊕", label: "Medical shop" }] },
  ],
  emergency_operator: [
    { section: "Network operations", items: networkItems.filter((item) => item.to !== "/shop") },
  ],
  hospital_admin: [
    { section: "Hospital operations", items: networkItems.filter((item) => item.to !== "/shop") },
  ],
  pharmacist: [
    { section: "Facility operations", items: [
      { to: "/dashboard", icon: "⊞", label: "Dashboard" },
      { to: "/inventory", icon: "▦", label: "My inventory" },
      { to: "/shop", icon: "⊕", label: "Pharmacy" },
    ] },
  ],
  shop_owner: [
    { section: "Donor operations", items: [
      { to: "/dashboard", icon: "⊞", label: "Dashboard" },
      { to: "/inventory", icon: "▦", label: "My inventory" },
      { to: "/shop", icon: "⊕", label: "Medical shop" },
    ] },
  ],
  supplier: [
    { section: "Supply operations", items: [
      { to: "/dashboard", icon: "⊞", label: "Dashboard" },
      { to: "/inventory", icon: "▦", label: "My inventory" },
    ] },
  ],
}

function labelRole(role: string) {
  return role.split("_").map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ")
}

export function Sidebar() {
  const navigate = useNavigate()
  const { data: user } = useCurrentUser()
  const role = user?.role ?? ""
  const canViewEmergencies = ["system_admin", "emergency_operator", "hospital_admin"].includes(role)
  const { data: emergencies = [] } = useEmergencies(canViewEmergencies)
  const activeEmergencyCount = emergencies.filter(
    (emergency) => emergency.emergency_status !== "RESOLVED" && emergency.emergency_status !== "CLOSED"
  ).length
  const sections = sectionsByRole[role] ?? [
    { section: "Workspace", items: [{ to: "/dashboard", icon: "⊞", label: "Dashboard" }] },
  ]

  function logout() {
    localStorage.removeItem("aegisflow_token")
    navigate("/login")
  }

  return (
    <aside style={{ width: 224 }} className="bg-white border-r border-border flex flex-col flex-shrink-0 h-full">
      <div className="flex items-center gap-2.5 px-4 py-4 border-b border-border">
        <div className="w-8 h-8 bg-blue-700 rounded-lg flex items-center justify-center flex-shrink-0">
          <span className="text-white text-sm font-bold">A</span>
        </div>
        <div>
          <div className="text-[14px] font-semibold text-ink">AegisFlow</div>
          <div className="text-[10px] text-ink-faint">Healthcare Intelligence</div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto py-2">
        {sections.map((section) => (
          <div key={section.section} className="px-2 mb-1">
            <div className="text-[10px] text-ink-faint uppercase tracking-[0.5px] px-2 py-2">{section.section}</div>
            {section.items.map((item) => {
              const badgeCount = item.to === "/emergency" ? activeEmergencyCount : undefined
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
                >
                  <span className="text-[15px] w-5 text-center">{item.icon}</span>
                  <span className="flex-1">{item.label}</span>
                  {badgeCount !== undefined && badgeCount > 0 && (
                    <span className={`nav-badge nav-badge-${item.badgeType ?? "red"}`}>{badgeCount}</span>
                  )}
                </NavLink>
              )
            })}
          </div>
        ))}
      </nav>

      <div className="p-3 border-t border-border">
        <div className="flex items-center gap-2 p-2 rounded hover:bg-surface-muted group">
          <div className="w-7 h-7 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700 text-[11px] font-semibold flex-shrink-0">
            {user?.name?.slice(0, 2).toUpperCase() || "AF"}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[12px] font-medium text-ink truncate">{user?.name ?? "Loading user…"}</div>
            <div className="text-[10px] text-ink-faint">{user?.role ? labelRole(user.role) : "Role loading"}</div>
          </div>
          <button onClick={logout} className="text-[10px] text-ink-faint hover:text-ink opacity-0 group-hover:opacity-100 transition-opacity">Out</button>
        </div>
      </div>
    </aside>
  )
}
