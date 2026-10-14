# Matriz de trazabilidad (REQM)

Une cada requisito de [requisitos.md](requisitos.md) con el código que lo implementa, las pruebas que lo verifican y los issues/PRs donde cambió. **B#** = issue/PR del backend, **F#** = del frontend.

Se actualiza en el mismo PR que toca un requisito (lo pide el checklist de la plantilla). En la auditoría PPQA de cada milestone se revisa que no haya requisitos *Hecho* sin prueba.

| Req. | Backend | Frontend | Pruebas | Issues / PRs |
|---|---|---|---|---|
| RF-01 | `routers/auth.py` (`register-patient`) | `patient-register` | `test_registro_valida_fecha_de_nacimiento` | |
| RF-02 | `routers/auth.py` (`register-doctor`), `routers/doctores.py` (`/activar`) | `doctor-register` | `test_registro_de_medico_queda_pendiente_y_no_puede_entrar`, `test_paciente_no_puede_activar_medicos` | |
| RF-03 | `routers/doctores.py` (`/biometria`), `routers/pacientes.py` | `biometric-enroll` (`/mi-rostro`) | `test_paciente_registra_su_propio_rostro`, `test_medico_solo_edita_su_propia_biometria`, `test_nadie_reemplaza_el_rostro_de_otro_medico` | |
| RF-04 | `routers/auth.py` (`facial-login`), `core/biometria.py` | `login`, `services/biometric.service.ts` | `test_login_facial_correcto`, `test_login_facial_rechaza_vector_de_un_solo_valor`, `test_login_facial_no_revela_si_el_correo_existe`, `test_login_facial_respeta_el_rol` | |
| RF-05 | `routers/auth.py` (`login`) | `login` | `LoginComponent con autocompletado` | F#6, F#8 |
| RF-06 | `core/security.py` | `guards/auth.guard.ts`, `interceptors/auth.interceptor.ts` | `AuthGuard`, `AuthInterceptor`, `AuthService` (frontend) | |
| RF-07 | `routers/citas.py` (`POST /`) | `appointment-book` (`/agendar-cita`) | `test_paciente_no_agenda_a_nombre_de_otro`, `HORARIOS de citas` | F#4, F#7 |
| RF-08 | `routers/citas.py` (`validar_horario`) | `appointment-book` (fecha mínima) | `test_no_se_agenda_en_el_pasado`, `test_no_se_cruza_el_horario_del_medico`, `test_cita_cancelada_libera_el_horario` | B#11, B#12 |
| RF-09 | `routers/citas.py` (`/doctor/{id}`) | `dashboard` (`filtrarCitas`) | `test_medico_no_ve_agenda_de_otro_medico`, `filtrarCitas del panel del doctor` | F#5, F#9 |
| RF-10 | `routers/citas.py` (`/paciente/{id}`) | `patient-dashboard` | `test_listar_citas_devuelve_solo_las_propias`, `test_cita_muestra_edad_real_o_nada` | |
| RF-11 | `routers/citas.py` (`PATCH /estado`) | `expedient-editor` | — falta prueba | |
| RF-12 | — | — | — | pendiente de issue |
| RF-13 | `routers/expedientes.py` | `expedient-editor` | `test_expediente_lo_firma_el_medico_del_token`, `test_expediente_nuevo_no_inventa_alergias_ni_posologia` | |
| RF-14 | `routers/expedientes.py`, `routers/pacientes.py` | `expedient` | `test_paciente_ve_lo_suyo`, `test_paciente_no_ve_datos_de_otro_paciente`, `test_paciente_incluye_resumen_clinico_real` | |
| RF-15 | `routers/expedientes.py` (`/recientes`) | `dashboard` | `test_consultas_recientes_solo_del_medico` | |
| RF-16 | `routers/llamadas.py` | `patient-dashboard`, `dashboard` | `test_llamadas_solo_entre_participantes` | |
| RF-17 | `main.py` (WebSocket) | `services/webrtc.service.ts`, `videocall` | `test_websocket_sin_token_se_cierra`, `test_websocket_no_permite_suplantar_a_otro_usuario`, `test_websocket_con_token_propio_recibe_mensajes` | |
| RF-18 | `routers/llamadas.py` (`terminar`) | `videocall` | — falta prueba | |
| RF-19 | `routers/freepbx.py`, `db/freepbx.py` | — | — falta prueba (requiere FreePBX) | |
| RF-20 | `routers/webhooks.py` | — | `test_webhooks_exigen_token` | |
| RNF-01 | `core/security.py` | `interceptors/auth.interceptor.ts` | `test_sin_token_responde_401`, `test_token_falso_responde_401` | |
| RNF-02 | `core/security.py` | `services/biometric.service.ts` | `test_paciente_no_modifica_ni_borra_lo_ajeno` y el resto de `test_seguridad.py` | |
| RNF-03 | `routers/*` | `expedient`, `patient-dashboard` | `test_datos_clinicos.py` | |
| RNF-04 | `migrations/`, `app/requirements.txt` | `package-lock.json` | `test_base_nueva_queda_igual_a_los_modelos`, `test_downgrade_completo_funciona` | |
| RNF-05 | `.github/workflows/ci.yml` | `.github/workflows/ci.yml` | El CI mismo | B#13, F#10 |
| RNF-06 | `Dockerfile`, `docker-compose.yml`, `core/config.py` | — | Job `docker` del CI | |
| RNF-07 | `routers/auth.py` (`facial-login`) | `services/biometric.service.ts` | Medición por API (p95 5 ms) | B#15 |
| RNF-08 | — | Tailwind responsive | PA-11 (iframe 360 px, 8 pantallas) | F#16, F#17 |
| RNF-09 | `core/config.py`, `db/seeder.py` | `environments/environment.prod.ts` | — falta prueba | B#9, B#10 |

## Huecos detectados

Requisitos sin prueba o sin implementar; cada uno se registra como issue de la fase 4:

- RF-11, RF-18, RF-19, RNF-09: sin prueba automática.
- RF-12: no implementado.
- RNF-07: falta medir la detección facial en el navegador (con cámara).
