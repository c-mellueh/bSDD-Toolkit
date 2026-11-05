/** Pill-shaped toggle used instead of checkboxes throughout the app (Checkbox-compatible props). */
import { Switch, type SwitchProps } from "@mantine/core";

export interface ToggleProps extends Omit<SwitchProps, "radius"> {
  /** Partially on (e.g. some children selected): shown on, in a lighter colour. */
  indeterminate?: boolean;
}

export function Toggle({ indeterminate, checked, color, styles, ...rest }: ToggleProps) {
  const partial = !!indeterminate && !checked;
  return (
    <Switch
      radius="xl"
      checked={checked || partial}
      color={partial ? "blue.3" : color}
      title={partial ? "…" : rest.title}
      styles={{ body: { alignItems: "center" }, ...(styles as object) }}
      {...rest}
    />
  );
}
