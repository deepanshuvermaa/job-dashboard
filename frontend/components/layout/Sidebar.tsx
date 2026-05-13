"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

const NAV = [
  {
    label: "MAIN",
    items: [
      { name: "Home", href: "/dashboard", d: "M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z M9 22V12h6v10" },
      { name: "Jobs", href: "/jobs", d: "M2 7h20v14H2z M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16" },
      { name: "Applications", href: "/jobs/applications", d: "M22 11.08V12a10 10 0 11-5.93-9.14 M22 4L12 14.01l-3-3" },
      { name: "Evaluations", href: "/jobs/evaluations", d: "M18 20V10 M12 20V4 M6 20v-6" },
      { name: "Portals", href: "/jobs/portals", d: "M12 2a10 10 0 100 20 10 10 0 000-20z M2 12h20 M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" },
    ],
  },
  {
    label: "OUTREACH",
    items: [
      { name: "Cold Email", href: "/outreach", d: "M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z M22 6l-10 7L2 6" },
      { name: "Recruiters", href: "/recruiters", d: "M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2 M9 3a4 4 0 100 8 4 4 0 000-8z M23 21v-2a4 4 0 00-3-3.87 M16 3.13a4 4 0 010 7.75" },
      { name: "Hacks", href: "/hacks", d: "M13 2L3 14h9l-1 8 10-12h-9l1-8" },
    ],
  },
  {
    label: "TOOLS",
    items: [
      { name: "Resume", href: "/resume", d: "M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z M14 2v6h6 M16 13H8 M16 17H8" },
      { name: "Profile", href: "/profile", d: "M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2 M12 3a4 4 0 100 8 4 4 0 000-8z" },
      { name: "Settings", href: "/settings", d: "M12 15a3 3 0 100-6 3 3 0 000 6z M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="w-[240px] h-screen fixed left-0 top-0 z-30 flex flex-col bg-eggshell border-r border-chalk">
      {/* Logo */}
      <div className="px-5 pt-6 pb-5">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-obsidian rounded-badge flex items-center justify-center">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#fdfcfc" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <span className="text-[20px] tracking-tight text-obsidian font-display">JobFlow</span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 overflow-y-auto">
        {NAV.map((group) => (
          <div key={group.label} className="mb-5">
            <p className="px-3 mb-2 text-label text-gravel uppercase">{group.label}</p>
            <ul className="space-y-px">
              {group.items.map((item) => {
                const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
                return (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className={`flex items-center gap-2.5 px-3 py-[7px] rounded-lg text-[13px] transition-colors ${
                        active
                          ? "bg-powder text-obsidian font-medium"
                          : "text-gravel hover:text-obsidian hover:bg-powder"
                      }`}
                    >
                      <svg className="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <path d={item.d} />
                      </svg>
                      {item.name}
                      {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-obsidian" />}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* User */}
      <div className="px-4 py-4 border-t border-chalk">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-obsidian flex items-center justify-center text-[12px] font-semibold text-eggshell">
            {user?.full_name?.[0]?.toUpperCase() || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[13px] text-obsidian truncate">{user?.full_name || "User"}</p>
            <p className="text-[10px] text-gravel truncate">{user?.email}</p>
          </div>
          <button onClick={logout} className="text-slate hover:text-obsidian transition-colors p-1" title="Sign out">
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4 M16 17l5-5-5-5 M21 12H9" />
            </svg>
          </button>
        </div>
      </div>
    </aside>
  );
}
