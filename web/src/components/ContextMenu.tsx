import { Menu } from "@mantine/core";
import { create } from "zustand";
import type { ReactNode } from "react";

export interface MenuItem {
  label: string;
  icon?: ReactNode;
  shortcut?: string;
  onClick: () => void;
  disabled?: boolean;
  color?: string;
  divider?: boolean;
}

interface MenuState {
  x: number;
  y: number;
  items: MenuItem[] | null;
  open: (e: { clientX: number; clientY: number; preventDefault: () => void }, items: MenuItem[]) => void;
  close: () => void;
}

export const useContextMenu = create<MenuState>((set) => ({
  x: 0,
  y: 0,
  items: null,
  open: (e, items) => {
    e.preventDefault();
    set({ x: e.clientX, y: e.clientY, items });
  },
  close: () => set({ items: null }),
}));

export function ContextMenuHost() {
  const { x, y, items, close } = useContextMenu();
  return (
    <Menu opened={!!items} onChange={(o) => !o && close()} position="bottom-start" offset={2} withinPortal shadow="md" closeOnItemClick>
      <Menu.Target>
        <div style={{ position: "fixed", left: x, top: y, width: 1, height: 1 }} />
      </Menu.Target>
      <Menu.Dropdown>
        {(items ?? []).map((item, i) =>
          item.divider ? (
            <Menu.Divider key={i} />
          ) : (
            <Menu.Item
              key={i}
              leftSection={item.icon}
              rightSection={item.shortcut ? <span style={{ fontSize: 11, opacity: 0.6 }}>{item.shortcut}</span> : undefined}
              onClick={() => {
                close();
                item.onClick();
              }}
              disabled={item.disabled}
              color={item.color}
            >
              {item.label}
            </Menu.Item>
          ),
        )}
      </Menu.Dropdown>
    </Menu>
  );
}

export const divider: MenuItem = { label: "", onClick: () => undefined, divider: true };
