# Rprojects

## Migrar un repo externo (ej. CursorCompras) a tu Git Server

Este repositorio ahora incluye el script `migrar_repo_a_git_server.sh` para copiar un repositorio completo (ramas, tags y refs) desde GitHub hacia tu servidor Git interno.

### Uso rápido

```bash
./migrar_repo_a_git_server.sh \
  https://github.com/acarmona-debug/CursorCompras.git \
  git@gitserver:equipo/CursorCompras.git
```

### Qué hace

1. Clona el repo origen en modo `--mirror`.
2. Apunta el push al repo destino.
3. Hace `git push --mirror` para transferir todo.

### Requisitos

- Acceso de red al repo de origen.
- Permisos de escritura al repo destino en tu Git server.
- `git` instalado.

### Nota

Si tu repo destino no existe, créalo primero en tu Git server (vacío, sin README inicial) y luego ejecuta el script.
