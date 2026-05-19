# Instrucciones de prueba API

## Base URL
- Local: http://localhost:8000
- Todas las rutas requieren slash final.

## Autenticacion y token
- El login genera un token.
- Enviar token en header:
  - Authorization: Token <token>
- No usar Bearer.

## Formato de requests
- Content-Type: application/json
- Body en JSON.

---

## Endpoints de autenticacion

### POST /api/login/
**Token:** no

**Request**
```json
{
  "email": "usuario@correo.com",
  "contrasena": "mi_password"
}
```

**200 OK**
```json
{
  "token": "0f1a...",
  "usuario": {
    "usuario_id": 1,
    "nombre": "Juan Perez",
    "email": "usuario@correo.com",
    "grupo": "LICENCIATURA",
    "rol": "USUARIO"
  }
}
```

**400 Bad Request** (credenciales invalidas)
```json
{
  "non_field_errors": ["Credenciales invalidas"]
}
```

---

### POST /api/logout/
**Token:** si

**Request**
```json
{}
```

**204 No Content**

**401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Endpoints de usuarios

### POST /api/usuarios/
**Token:** no (registro publico)
- Si envias token ADMIN, puedes crear usuarios con rol ADMIN.

**Request**
```json
{
  "nombre": "Ana Lopez",
  "email": "ana@correo.com",
  "contrasena": "miclave123",
  "grupo": "LICENCIATURA"
}
```

**Request (crear admin con token ADMIN)**
```json
{
  "nombre": "Admin Uno",
  "email": "admin@correo.com",
  "contrasena": "miclave123",
  "grupo": "MAESTRIA",
  "rol": "ADMIN"
}
```

**201 Created**
```json
{
  "usuario_id": 2,
  "nombre": "Ana Lopez",
  "email": "ana@correo.com",
  "grupo": "LICENCIATURA",
  "rol": "USUARIO"
}
```

**400 Bad Request** (validacion)
```json
{
  "email": ["usuario con este email ya existe."]
}
```

**400 Bad Request** (rol admin en registro publico)
```json
{
  "rol": ["No es posible asignar rol ADMIN en registro publico"]
}
```

---

### GET /api/usuarios/mi-perfil/
**Token:** si

**200 OK**
```json
{
  "usuario_id": 2,
  "nombre": "Ana Lopez",
  "email": "ana@correo.com",
  "grupo": "LICENCIATURA",
  "rol": "USUARIO"
}
```

**401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### PATCH /api/usuarios/mi-perfil/
**Token:** si

**Request**
```json
{
  "nombre": "Ana Lopez Garcia",
  "contrasena": "nuevaClave123",
  "grupo": "MAESTRIA"
}
```

**200 OK**
```json
{
  "usuario_id": 2,
  "nombre": "Ana Lopez Garcia",
  "email": "ana@correo.com",
  "grupo": "MAESTRIA",
  "rol": "USUARIO"
}
```

---

### DELETE /api/usuarios/mi-perfil/
**Token:** si

**204 No Content**

---

### GET /api/usuarios/
**Token:** si (ADMIN)

**200 OK**
```json
[
  {
    "usuario_id": 1,
    "nombre": "Juan Perez",
    "email": "usuario@correo.com",
    "grupo": "LICENCIATURA",
    "rol": "USUARIO"
  }
]
```

**403 Forbidden**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### GET /api/usuarios/{id}/
**Token:** si (ADMIN)

**200 OK**
```json
{
  "usuario_id": 3,
  "nombre": "Pedro Ruiz",
  "email": "pedro@correo.com",
  "grupo": "PREPA",
  "rol": "USUARIO"
}
```

---

### PATCH /api/usuarios/{id}/
**Token:** si (ADMIN)

**Request**
```json
{
  "rol": "ADMIN",
  "grupo": "DOCTORADO",
  "is_active": true
}
```

**200 OK**
```json
{
  "usuario_id": 3,
  "nombre": "Pedro Ruiz",
  "email": "pedro@correo.com",
  "grupo": "DOCTORADO",
  "rol": "ADMIN",
  "is_active": true
}
```

---

### DELETE /api/usuarios/{id}/
**Token:** si (ADMIN)

**204 No Content**

---

## Endpoints de examenes

### GET /api/examenes/
**Token:** no

**200 OK**
```json
[
  {
    "examen_id": 1,
    "tipo": "VARK",
    "nombre": "Test VARK",
    "descripcion": "Estilos de aprendizaje VARK",
    "preguntas": [
      {
        "pregunta_id": 1,
        "texto": "Estas ayudando a alguien a llegar...",
        "respuestas": [
          {"respuesta_id": 1, "texto": "Le dibuja un mapa..."}
        ]
      }
    ]
  }
]
```

---

### GET /api/examenes/{id}/
**Token:** no

**200 OK**
```json
{
  "examen_id": 1,
  "tipo": "VARK",
  "nombre": "Test VARK",
  "descripcion": "Estilos de aprendizaje VARK",
  "preguntas": []
}
```

---

### POST /api/examenes/{id}/iniciar/
**Token:** no (si el usuario esta autenticado, se asocia)

**Request**
```json
{}
```

**201 Created**
```json
{
  "examen_presentado": {
    "examen_presentado_id": 10,
    "examen_id": 1,
    "usuario_id": 2,
    "grupo": "LICENCIATURA",
    "fecha_creacion": "2026-05-09T12:00:00Z",
    "estado": "EN_PROCESO"
  },
  "examen": {
    "examen_id": 1,
    "tipo": "VARK",
    "nombre": "Test VARK",
    "descripcion": "Estilos de aprendizaje VARK",
    "preguntas": [
      {
        "pregunta_id": 1,
        "texto": "Estas ayudando a alguien a llegar...",
        "respuestas": [
          {"respuesta_id": 1, "texto": "Le dibuja un mapa..."}
        ]
      }
    ]
  }
}
```

---

## Endpoints de examenes presentados

### GET /api/examenes-presentados/
**Token:** si (ADMIN)

**200 OK**
```json
[
  {
    "examen_presentado_id": 10,
    "examen": {
      "examen_id": 1,
      "tipo": "VARK",
      "nombre": "Test VARK",
      "descripcion": "Estilos de aprendizaje VARK"
    },
    "usuario_id": 2,
    "grupo": "LICENCIATURA",
    "fecha_creacion": "2026-05-09T12:00:00Z",
    "estado": "FINALIZADO",
    "resultado_vark": {
      "v": 4,
      "a": 6,
      "r": 2,
      "k": 4,
      "arquetipo": {
        "arquetipo_id": 1,
        "codigo": "A",
        "nombre": "Aural / Auditivo",
        "descripcion": "Aprende mejor escuchando..."
      }
    },
    "resultado_jung": null
  }
]
```

---

### GET /api/examenes-presentados/usuario/{usuario_id}/
**Token:** si
- ADMIN: puede consultar cualquier usuario_id
- USUARIO: solo su propio usuario_id

**200 OK**
```json
[
  {
    "examen_presentado_id": 10,
    "examen": {
      "examen_id": 1,
      "tipo": "VARK",
      "nombre": "Test VARK",
      "descripcion": "Estilos de aprendizaje VARK"
    },
    "usuario_id": 2,
    "grupo": "LICENCIATURA",
    "fecha_creacion": "2026-05-09T12:00:00Z",
    "estado": "FINALIZADO",
    "resultado_vark": {
      "v": 4,
      "a": 6,
      "r": 2,
      "k": 4,
      "arquetipo": {
        "arquetipo_id": 1,
        "codigo": "A",
        "nombre": "Aural / Auditivo",
        "descripcion": "Aprende mejor escuchando..."
      }
    },
    "resultado_jung": null
  }
]
```

**403 Forbidden**
```json
{
  "detail": "No tienes permiso para realizar esta accion."
}
```

---

### GET /api/examenes-presentados/grupo/{grupo}/
**Token:** si (ADMIN)

**200 OK**
```json
[
  {
    "examen_presentado_id": 10,
    "examen": {
      "examen_id": 1,
      "tipo": "VARK",
      "nombre": "Test VARK",
      "descripcion": "Estilos de aprendizaje VARK"
    },
    "usuario_id": 2,
    "grupo": "LICENCIATURA",
    "fecha_creacion": "2026-05-09T12:00:00Z",
    "estado": "FINALIZADO",
    "resultado_vark": {
      "v": 4,
      "a": 6,
      "r": 2,
      "k": 4,
      "arquetipo": {
        "arquetipo_id": 1,
        "codigo": "A",
        "nombre": "Aural / Auditivo",
        "descripcion": "Aprende mejor escuchando..."
      }
    },
    "resultado_jung": null
  }
]
```

---

### POST /api/examenes-presentados/{id}/enviar/
**Token:** no (si el examen tiene usuario, valida ownership)

**Request**
```json
{
  "respuestas": [
    {"pregunta_id": 1, "respuesta_id": 2},
    {"pregunta_id": 2, "respuesta_id": 8}
  ]
}
```

**200 OK (VARK)**
```json
{
  "examen_presentado": {
    "examen_presentado_id": 10,
    "examen_id": 1,
    "usuario_id": 2,
    "grupo": "LICENCIATURA",
    "fecha_creacion": "2026-05-09T12:00:00Z",
    "estado": "FINALIZADO"
  },
  "resultado": {
    "v": 4,
    "a": 6,
    "r": 2,
    "k": 4,
    "arquetipo": {
      "arquetipo_id": 1,
      "codigo": "A",
      "nombre": "Aural / Auditivo",
      "descripcion": "Aprende mejor escuchando..."
    }
  }
}
```

**200 OK (JUNG)**
```json
{
  "examen_presentado": {
    "examen_presentado_id": 20,
    "examen_id": 2,
    "usuario_id": null,
    "grupo": null,
    "fecha_creacion": "2026-05-09T12:00:00Z",
    "estado": "FINALIZADO"
  },
  "resultado": {
    "i_count": 3,
    "e_count": 5,
    "n_count": 6,
    "s_count": 2,
    "t_count": 4,
    "f_count": 4,
    "j_count": 5,
    "p_count": 3,
    "tipo_personalidad": "ENFJ",
    "arquetipo": {
      "arquetipo_id": 5,
      "codigo": "ENFJ",
      "nombre": "El Profesor",
      "descripcion": "Carismatico, atento..."
    }
  }
}
```

**400 Bad Request** (estado no valido)
```json
{
  "detalle": "El examen no esta en estado EN_PROCESO"
}
```

**400 Bad Request** (respuesta no corresponde)
```json
{
  "detalle": "Respuesta no corresponde al examen"
}
```

**403 Forbidden** (no ownership)
```json
{
  "detalle": "No tienes permiso para enviar este examen"
}
```

**404 Not Found**
```json
{
  "detalle": "Examen presentado no encontrado"
}
```

---

## Analitica (admin)

### GET /api/analitica/resumen/
**Token:** si (ADMIN)

**Query params**
- examen_id
- usuario_id
- grupo
- tipo
- rol
- estado
- arquetipo
- fecha_inicio (YYYY-MM-DD)
- fecha_fin (YYYY-MM-DD)

**200 OK**
```json
{
  "total": 10,
  "por_estado": [{"estado": "FINALIZADO", "total": 7}],
  "por_grupo": [{"grupo": "LICENCIATURA", "total": 5}],
  "por_tipo": [{"examen__tipo": "VARK", "total": 6}],
  "por_rol": [{"usuario__rol": "USUARIO", "total": 8}],
  "arquetipos_vark": [{"resultado_vark__arquetipo__codigo": "A", "total": 3}],
  "arquetipos_jung": [{"resultado_jung__arquetipo__codigo": "INTJ", "total": 2}]
}
```

**400 Bad Request** (fecha invalida)
```json
{
  "detalle": "fecha_inicio debe ser YYYY-MM-DD"
}
```

**403 Forbidden**
```json
{
  "detail": "You do not have permission to perform this action."
}
```
