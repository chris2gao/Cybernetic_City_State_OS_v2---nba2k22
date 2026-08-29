# window_role_binding loader (Stage 04 fixture overlay)

Explicit loader entry for the composition mechanism. Invocation is Human or an
authorized task executor; nothing here runs on a timer.

1. Read `01_os/02_boot/window_role_binding/boot_v1.yml`.
2. Load every `load_order` path in order; a missing path is fail-closed.
3. Run the declared validator; a non-zero exit is fail-closed.
4. Emit the receipt fields the boot manifest declares.

Registration is `01_os/05_registry/window_role_binding_v1.yml`.
