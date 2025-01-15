# app_principal/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .sheets_helper import connect_to_sheets
import json
import gspread
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime
import bcrypt
from django.urls import reverse
import logging


# Vista para manejar el inicio de sesión
def login_page(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos.'})

        usuario = data.get('usuario')
        password = data.get('password')

        # Conectar con Google Sheets
        client = connect_to_sheets()
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
        worksheet = sheet.worksheet('Usuarios')  # Asegúrate de que la hoja se llame 'Usuarios'

        # Verificar si las credenciales coinciden
        records = worksheet.get_all_records()
        for record in records:
            if record['Usuario'] == usuario:
                hashed_password = record['Contraseña'].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    # Guardar 'usuario' en la sesión
                    request.session['usuario'] = usuario
                    return JsonResponse({'status': 'success', 'message': 'Inicio de sesión exitoso'})

        # Si no coinciden
        return JsonResponse({'status': 'error', 'message': 'Usuario o contraseña incorrectos'})

    return render(request, 'login.html')


# Vista para manejar el registro de usuarios
def signup(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos.'})

        persona_responsable = data.get('persona_responsable')
        institucion = data.get('institucion')
        area = data.get('area')
        usuario = data.get('usuario')
        password = data.get('password')

        # Validaciones adicionales pueden ser añadidas aquí

        # Conectar con Google Sheets
        client = connect_to_sheets()
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
        worksheet = sheet.worksheet('Usuarios')  # Asegúrate de que la hoja se llame 'Usuarios'

        # Verificar si el usuario ya existe
        existing_users = worksheet.col_values(4)  # 'Usuario' está en la columna D (índice 4)
        if usuario in existing_users:
            return JsonResponse({'status': 'error', 'message': f'El usuario "{usuario}" ya existe. Por favor, elige otro nombre de usuario.'})

        # Hashear la contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insertar una nueva fila en la hoja
        worksheet.append_row([persona_responsable, institucion, area, usuario, hashed_password])
        return JsonResponse({'status': 'success', 'message': 'Usuario registrado con éxito.'})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


# Vista para generar reportes
def generate_report(request):
    if request.method == 'GET':
        # Conectar con Google Sheets
        client = connect_to_sheets()
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
        worksheet = sheet.worksheet('Salas')  # Asegúrate de que el nombre de la hoja sea 'Salas'

        # Obtener todas las salas
        salas = worksheet.col_values(1)[1:]  # Supone que la primera fila es encabezado

        return render(request, 'generate_report.html', {'salas': salas})

    return redirect('login_page')


# API para obtener equipos basado en la sala seleccionada
def get_equipos(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos.'})
        
        sala = data.get('sala')
        
        if not sala:
            return JsonResponse({'status': 'error', 'message': 'No se proporcionó una sala.'})
        
        try:
            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            
            # Intentar acceder a la hoja con el nombre de la sala seleccionada
            try:
                worksheet = sheet.worksheet(sala)
            except gspread.WorksheetNotFound:
                return JsonResponse({'status': 'error', 'message': f'La sala "{sala}" no existe.'})
            
            # Obtener todos los valores de la primera columna, excluyendo el encabezado si existe
            equipos = worksheet.col_values(1)
            print(equipos)
            equipos = equipos[1:] if equipos else []
            print(equipos)
            # Filtrar equipos no vacíos
            equipos = [equipo.strip() for equipo in equipos if equipo.strip()]
            
            if not equipos:
                return JsonResponse({'status': 'error', 'message': f'No hay equipos registrados para la sala "{sala}".'})
            
            return JsonResponse({'status': 'success', 'equipos': equipos})
        
        except Exception as e:
            # Registrar el error para depuración (opcional)
            print(f'Error al obtener equipos para la sala "{sala}": {e}')
            return JsonResponse({'status': 'error', 'message': 'Ocurrió un error al obtener los equipos.'})
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


# API para generar reporte
def generar_reporte(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos.'})

        sala = data.get('sala')
        fechaInicio = data.get('fechaInicio')
        fechaFin = data.get('fechaFin')
        horasPorDia = data.get('horasPorDia')  # Lista de horas por día

        if not all([sala, fechaInicio, fechaFin, horasPorDia]):
            return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios.'})

        # Verificar que horasPorDia sea una lista y que su longitud coincida con el rango de días
        if not isinstance(horasPorDia, list):
            return JsonResponse({'status': 'error', 'message': 'Las horas por día deben ser una lista.'})

        # Calcular número de días
        date_format = "%Y-%m-%d"
        try:
            start_date = datetime.strptime(fechaInicio, date_format)
            end_date = datetime.strptime(fechaFin, date_format)
            delta = end_date - start_date
            num_days = delta.days + 1  # Inclusivo
            if num_days < 1:
                return JsonResponse({'status': 'error', 'message': 'La fecha de fin debe ser posterior a la fecha de inicio.'})
            if num_days > 7:
                return JsonResponse({'status': 'error', 'message': 'El rango de fechas no puede exceder 7 días.'})
            if len(horasPorDia) != num_days:
                return JsonResponse({'status': 'error', 'message': 'La cantidad de horas por día no coincide con el rango de fechas.'})
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Formato de fecha inválido.'})

        # Obtener información del usuario desde la sesión
        usuario = request.session.get('usuario')  # Asegúrate de que 'usuario' esté almacenado en la sesión
        if not usuario:
            return JsonResponse({'status': 'error', 'message': 'Usuario no autenticado.'})

        # Conectar con Google Sheets
        try:
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')

            # Obtener la hoja de usuarios
            usuarios_sheet = sheet.worksheet('Usuarios')  # Asegúrate de que la hoja se llame 'Usuarios'
            usuarios_records = usuarios_sheet.get_all_records()

            # Buscar el registro del usuario
            user_record = next((record for record in usuarios_records if record['Usuario'] == usuario), None)
            if not user_record:
                return JsonResponse({'status': 'error', 'message': 'Información del usuario no encontrada.'})

            # Actualización de nombres de columnas
            persona_responsable = user_record.get('PersonaResponsable', 'N/A')
            institucion = user_record.get('Institucion', 'N/A')
            area = user_record.get('Area', 'N/A')

            # Obtener la hoja de la sala seleccionada
            try:
                sala_sheet = sheet.worksheet(sala)
            except gspread.WorksheetNotFound:
                return JsonResponse({'status': 'error', 'message': f'La sala "{sala}" no existe.'})

            # Obtener equipos de la primera columna
            equipos = sala_sheet.col_values(1)  # Primera columna (A)
            equipos = [equipo.strip() for equipo in equipos if equipo.strip()]

            if not equipos:
                return JsonResponse({'status': 'error', 'message': f'No hay equipos registrados para la sala "{sala}".'})

            # Eliminar el primer elemento si es 'nombre:'
            if equipos:
                equipos = equipos[1:]

            # Calcular intervalo de tiempo
            intervalo_tiempo = f"{fechaInicio} - {fechaFin}"

            # Obtener Kv de cada equipo
            filas = sala_sheet.get_all_values()
            if not filas:
                return JsonResponse({'status': 'error', 'message': f'La hoja de la sala "{sala}" está vacía.'})

            encabezados = filas[0]
            try:
                kv_index = encabezados.index('Kwh')  # Índice de la columna 'Kwh'
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'No se encontró la columna "Kwh" en la hoja de la sala.'})

            total_kwh = 0
            consumo_por_dia = []  # Lista para almacenar consumo por día
            emisiones_por_dia = []  # Lista para almacenar emisiones por día

            # Primero, calcular total_kwh basado en equipos
            for equipo in equipos:
                # Buscar la fila correspondiente al equipo
                for fila in filas[1:]:
                    if fila[0].strip().lower() == equipo.strip().lower():
                        try:
                            kv = float(fila[kv_index])
                            total_kwh += kv
                        except (ValueError, IndexError):
                            # Manejar casos donde 'Kwh' no es válido o está ausente
                            pass
                        break

            # Ahora, calcular consumo_por_dia con el total_kwh correcto
            consumo_por_dia = [total_kwh * horas for horas in horasPorDia]

            # Calcular Consumo energético total
            consumo_energetico_kwh = sum(consumo_por_dia)

            # Calcular Emisiones de CO2 por día y total
            factor_emision = 0.18  # kg CO₂/kWh
            emisiones_por_dia = [consumo_dia * factor_emision for consumo_dia in consumo_por_dia]
            emisiones_co2_kg = sum(emisiones_por_dia)

            # Calcular Producción de residuos
            # Nueva lógica basada en la hoja 'Residuos'
            try:
                residuos_sheet = sheet.worksheet('Residuos')  # Asegúrate de que la hoja se llame 'Residuos'
                residuos_records = residuos_sheet.get_all_records()
            except gspread.WorksheetNotFound:
                return JsonResponse({'status': 'error', 'message': 'La hoja "Residuos" no existe.'})

            total_peso_residuos = 0
            for equipo in equipos:
                # Buscar el equipo en la hoja 'Residuos'
                equipo_record = next((res for res in residuos_records if res['Equipo'].strip().lower() == equipo.strip().lower()), None)
                if equipo_record:
                    try:
                        peso = float(equipo_record.get('Peso(kg)', 0))
                        total_peso_residuos += peso
                    except (ValueError, TypeError):
                        # Manejar casos donde 'Peso(kg)' no es válido o está ausente
                        pass
                else:
                    # Opcional: manejar equipos que no se encuentran en 'Residuos'
                    print(f'Equipo "{equipo}" no encontrado en la hoja "Residuos".')

            # Multiplicar la sumatoria del peso por el número de días
            produccion_residuos_kg = total_peso_residuos * num_days

            # Generar report number
            # Asumiendo que es un número incremental, buscar el último número en una hoja 'Reportes'
            try:
                reportes_sheet = sheet.worksheet('Reportes')  # Asegúrate de que la hoja 'Reportes' exista
                reportes = reportes_sheet.get_all_records()
                if reportes:
                    last_report = reportes[-1]
                    last_number = int(last_report.get('No.', '0'))
                    report_number = last_number + 1
                else:
                    report_number = 1
                # Registrar el nuevo reporte
                # Almacenar horasPorDia como una cadena separada por comas
                horas_por_dia_str = ','.join(map(str, horasPorDia))
                reportes_sheet.append_row([report_number, usuario, sala, fechaInicio, fechaFin, horas_por_dia_str])
            except gspread.WorksheetNotFound:
                # Si la hoja 'Reportes' no existe, crearla y añadir encabezados
                reportes_sheet = sheet.add_worksheet(title='Reportes', rows='100', cols='6')
                reportes_sheet.append_row(['No.', 'Usuario', 'Sala', 'Fecha Inicio', 'Fecha Fin', 'Horas Por Día'])
                report_number = 1
                horas_por_dia_str = ','.join(map(str, horasPorDia))
                reportes_sheet.append_row([report_number, usuario, sala, fechaInicio, fechaFin, horas_por_dia_str])
            except Exception as e:
                print(f'Error al generar número de reporte: {e}')
                return JsonResponse({'status': 'error', 'message': 'Error al generar el número de reporte.'})

            # ----------------------------
            # **Cálculo de X y N**
            # ----------------------------
            # a = 3
            a = 3

            # Calcular p
            promedio_consumo_diario = consumo_energetico_kwh / num_days if num_days > 0 else 0

            # Obtener valores de 'PConsumo'
            try:
                pconsumo_sheet = sheet.worksheet('PConsumo')  # Asegúrate de que la hoja se llame 'PConsumo'
                pconsumo_values = pconsumo_sheet.get_all_values()
                if not pconsumo_values or len(pconsumo_values) < 2:
                    return JsonResponse({'status': 'error', 'message': 'La hoja "PConsumo" no tiene datos suficientes.'})
                # Asumiendo que la primera fila es encabezado y la segunda fila contiene 'Baja' y 'Alta'
                baja_str = pconsumo_values[1][0]  # Columna Baja
                alta_str = pconsumo_values[1][1]  # Columna Alta
                baja_pconsumo = float(baja_str) if baja_str else 0
                alta_pconsumo = float(alta_str) if alta_str else 0
            except Exception as e:
                print(f'Error al obtener valores de PConsumo: {e}')
                return JsonResponse({'status': 'error', 'message': 'Error al obtener valores de PConsumo.'})

            # Determinar p
            if promedio_consumo_diario <= baja_pconsumo:
                p = 1
            elif promedio_consumo_diario >= alta_pconsumo:
                p = 3
            else:
                p = 2

            # Obtener valores de 'Salas' para c
            try:
                salas_sheet = sheet.worksheet('Salas')  # Asegúrate de que la hoja se llame 'Salas'
                salas_records = salas_sheet.get_all_records()
                sala_record = next((record for record in salas_records if record['Nombre'].strip().lower() == sala.strip().lower()), None)
                if not sala_record:
                    return JsonResponse({'status': 'error', 'message': f'Información de la sala "{sala}" no encontrada en "Salas".'})
                cbaja_str = sala_record.get('Cbaja', '0')
                calta_str = sala_record.get('CAlta', '0')
                cbaja = float(cbaja_str) if cbaja_str else 0
                calta = float(calta_str) if calta_str else 0
            except Exception as e:
                print(f'Error al obtener valores de Salas: {e}')
                return JsonResponse({'status': 'error', 'message': 'Error al obtener valores de Salas.'})

            # Determinar c
            produccion_residuos = produccion_residuos_kg
            if produccion_residuos <= cbaja:
                c = 1
            elif produccion_residuos >= calta:
                c = 3
            else:
                c = 2

            # Calcular X
            X = a * p * c

            # Determinar N
            if X <= 8:
                N = 'No significativo'
        
            else:
                N = 'Significativo'

            # ----------------------------

            # **Definir moderate y high**
            # Como en tu plantilla report.html estos valores son 12 y 27 respectivamente,
            # los definimos como constantes.
            moderate = 12
            high = 27

            # Preparar los datos para la plantilla
            report_data = {
                'usuario': usuario,
                'report_number': f"{report_number:05d}",  # Formatear con ceros a la izquierda
                'persona_responsable': persona_responsable,
                'institucion': institucion,
                'area': area,
                'sala_seleccionada': sala,
                'equipos': equipos,
                'intervalo_tiempo': intervalo_tiempo,
                'consumo_energetico_kwh': round(consumo_energetico_kwh, 2),
                'emisiones_co2_kg': round(emisiones_co2_kg, 2),
                'produccion_residuos_kg': round(produccion_residuos_kg, 2),
                'baja': baja_pconsumo,  # Actualizado para reflejar los valores obtenidos de PConsumo
                'moderate': moderate,     # Definido como constante
                'high': high,             # Definido como constante
                'horasPorDia': horasPorDia,  # Lista de horas por día
                'consumoPorDia': [round(c, 2) for c in consumo_por_dia],  # Lista de consumo por día
                'emisionesPorDia': [round(e, 2) for e in emisiones_por_dia],  # Lista de emisiones por día
                'X': round(X, 2),  # Agregado
                'N': N,            # Agregado
            }

            # Guardar los datos en la sesión
            request.session['report_data'] = report_data

            # Construir la URL de redirección usando 'reverse'
            redirect_url = reverse('view_report')  # Asegúrate de que el nombre de la ruta sea 'view_report'

            return JsonResponse({'status': 'success', 'redirect_url': redirect_url})

        except Exception as e:
            print(f'Error al generar reporte: {e}')
            return JsonResponse({'status': 'error', 'message': 'Ocurrió un error al generar el reporte.'})

    # Vista para mostrar el reporte
def view_report(request):
        # Obtener los datos del reporte desde la sesión
        report_data = request.session.get('report_data')

        if not report_data:
            # Si no hay datos, redirigir a la página de generar reporte
            return redirect('generate_report')

        # Extraer los datos
        usuario = report_data.get('usuario')
        report_number = report_data.get('report_number')
        persona_responsable = report_data.get('persona_responsable')
        institucion = report_data.get('institucion')
        area = report_data.get('area')
        sala_seleccionada = report_data.get('sala_seleccionada')
        equipos = report_data.get('equipos')
        intervalo_tiempo = report_data.get('intervalo_tiempo')
        consumo_energetico_kwh = report_data.get('consumo_energetico_kwh')
        emisiones_co2_kg = report_data.get('emisiones_co2_kg')
        produccion_residuos_kg = report_data.get('produccion_residuos_kg')
        baja = report_data.get('baja', 0)
        moderate = report_data.get('moderate', 0)
        high = report_data.get('high', 0)
        horasPorDia = report_data.get('horasPorDia', [])
        consumoPorDia = report_data.get('consumoPorDia', [])
        emisionesPorDia = report_data.get('emisionesPorDia', [])
        X = report_data.get('X', 0)  # Agregado
        N = report_data.get('N', 'N/A')  # Agregado

        context = {
            'usuario': usuario,
            'report_number': report_number,
            'persona_responsable': persona_responsable,
            'institucion': institucion,
            'area': area,
            'sala_seleccionada': sala_seleccionada,
            'equipos': equipos,
            'intervalo_tiempo': intervalo_tiempo,
            'consumo_energetico_kwh': consumo_energetico_kwh,
            'emisiones_co2_kg': emisiones_co2_kg,
            'produccion_residuos_kg': produccion_residuos_kg,
            'baja': baja,
            'moderate': moderate,
            'high': high,
            'horasPorDia': horasPorDia,  # Lista de horas por día
            'consumoPorDia': consumoPorDia,  # Lista de consumo por día
            'emisionesPorDia': emisionesPorDia,  # Lista de emisiones por día
            'X': X,  # Agregado
            'N': N,  # Agregado
        }

        # Limpiar los datos de la sesión después de usarlos
        del request.session['report_data']

        return render(request, 'report.html', context)
    
def manage_users(request):
    try:
        client = connect_to_sheets()
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
        usuarios_sheet = sheet.worksheet('Usuarios')
        usuarios_records = usuarios_sheet.get_all_records()

        # Preparar la lista de usuarios
        usuarios = []
        for record in usuarios_records:
            usuario = {
                'persona_responsable': record.get('PersonaResponsable', ''),
                'institucion': record.get('Institucion', ''),
                'area': record.get('Area', ''),
                'usuario': record.get('Usuario', ''),
                'contraseña': record.get('Contraseña', ''),
            }
            usuarios.append(usuario)

        context = {
            'usuarios': usuarios,
        }

        return render(request, 'manage_users.html', context)

    except Exception as e:
        print(f'Error al cargar usuarios: {e}')
        return render(request, 'manage_users.html', {'usuarios': [], 'error': 'Error al cargar los usuarios.'})


@csrf_exempt 
def edit_user(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            original_usuario = data.get('original_usuario')
            persona_responsable = data.get('persona_responsable')
            institucion = data.get('institucion')
            area = data.get('area')
            usuario = data.get('usuario')
            contraseña = data.get('contraseña')  # Puede ser null

            if not original_usuario:
                return JsonResponse({'status': 'error', 'message': 'Usuario original no proporcionado.'})

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            usuarios_sheet = sheet.worksheet('Usuarios')
            usuarios_records = usuarios_sheet.get_all_records()

            # Encontrar la fila del usuario original
            row_number = None
            for idx, record in enumerate(usuarios_records, start=2):  # start=2 porque la primera fila son encabezados
                if record.get('Usuario', '').strip().lower() == original_usuario.strip().lower():
                    row_number = idx
                    break

            if not row_number:
                return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado.'})

            # Actualizar los campos
            usuarios_sheet.update_cell(row_number, 1, persona_responsable)  # PersonaResponsable
            usuarios_sheet.update_cell(row_number, 3, institucion)  # Institución
            usuarios_sheet.update_cell(row_number, 4, area)  # Área
            usuarios_sheet.update_cell(row_number, 5, usuario)  # Usuario

            # Manejar la contraseña
            if contraseña:
                # Encriptar la contraseña antes de almacenarla
                hashed_pw = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                usuarios_sheet.update_cell(row_number, 6, hashed_pw)  # Contraseña
            # Si contraseña es null, no hacer nada para mantener la existente

            return JsonResponse({'status': 'success', 'message': 'Usuario actualizado exitosamente.'})

        except Exception as e:
            print(f'Error al editar usuario: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error al editar el usuario.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@csrf_exempt  
def delete_user(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            usuario = data.get('usuario')

            if not usuario:
                return JsonResponse({'status': 'error', 'message': 'Usuario no proporcionado.'})

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            usuarios_sheet = sheet.worksheet('Usuarios')
            usuarios_records = usuarios_sheet.get_all_records()

            # Encontrar la fila del usuario
            row_number = None
            for idx, record in enumerate(usuarios_records, start=2):  # start=2 porque la primera fila son encabezados
                if record.get('Usuario', '').strip().lower() == usuario.strip().lower():
                    row_number = idx
                    break

            if not row_number:
                return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado.'})

            # Eliminar la fila
            usuarios_sheet.delete_rows(row_number)

            return JsonResponse({'status': 'success', 'message': 'Usuario eliminado exitosamente.'})

        except Exception as e:
            print(f'Error al eliminar usuario: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error al eliminar el usuario.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})
    
@csrf_exempt
def delete_all_users(request):
    try:
        client = connect_to_sheets()
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
        usuarios_sheet = sheet.worksheet('Usuarios')

        # Obtener todas las filas excepto la primera (encabezados)
        all_rows = usuarios_sheet.get_all_values()
        if len(all_rows) <= 1:
            return JsonResponse({'status': 'error', 'message': 'No hay usuarios para eliminar.'})

        # Eliminar todas las filas excepto la primera
        usuarios_sheet.batch_clear(['A2:F'])  # Asumiendo que hay 6 columnas: A-F

        return JsonResponse({'status': 'success', 'message': 'Todos los usuarios han sido eliminados exitosamente.'})

    except Exception as e:
        print(f'Error al eliminar todos los usuarios: {e}')
        return JsonResponse({'status': 'error', 'message': 'Error al eliminar todos los usuarios.'})
    
def manage_salas(request):
    try:
        client = connect_to_sheets()
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
        salas_sheet = sheet.worksheet('Salas')  # Asegúrate de que esta hoja exista
        salas_records = salas_sheet.get_all_records()

        # Preparar la lista de salas
        salas = []
        for record in salas_records:
            sala = {
                'nombre': record.get('Nombre', ''),
                'cbaja': record.get('CBaja', ''),
                'calta': record.get('CAlta', ''),
            }
            salas.append(sala)

        context = {
            'salas': salas,
        }

        return render(request, 'manage_salas.html', context)

    except Exception as e:
        print(f'Error al cargar salas: {e}')
        return render(request, 'manage_salas.html', {'salas': [], 'error': 'Error al cargar las salas.'})


@csrf_exempt
def add_sala(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            cbaja = data.get('cbaja')
            calta = data.get('calta')

            if not nombre or not cbaja or not calta:
                return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios.'})

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            salas_sheet = sheet.worksheet('Salas')

            # Verificar si ya existe una hoja con el mismo nombre
            try:
                existing_sheet = sheet.worksheet(nombre)
                return JsonResponse({'status': 'error', 'message': f'Ya existe una sala con el nombre "{nombre}".'})
            except:
                pass  # Si no existe, continuar

            # Añadir la nueva sala
            salas_sheet.append_row([nombre, cbaja, calta])

            # Crear una nueva hoja para la Sala con las columnas especificadas
            headers = [
                'Nombre', 'Marca', 'Modelo', 'Serie', 'Clasificación por riesgo',
                'Registro INVIMA', 'Lote', 'Vida útil', 'Voltaje (V)',
                'Corriente (A)', 'Potencia (W)', 'Kwh',
                'Consumibles (Desechables)', 'Accesorios (No desechables)'
            ]

            # Crear la nueva hoja
            new_sheet = sheet.add_worksheet(title=nombre, rows=100, cols=14)  # Puedes ajustar filas y columnas según necesidad
            new_sheet.append_row(headers)

            return JsonResponse({'status': 'success', 'message': 'Sala agregada exitosamente.'})

        except Exception as e:
            print(f'Error al agregar sala: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error al agregar la sala.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@csrf_exempt
def edit_sala(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            original_nombre = data.get('original_nombre')
            nombre = data.get('nombre')
            cbaja = data.get('cbaja')
            calta = data.get('calta')

            if not original_nombre:
                return JsonResponse({'status': 'error', 'message': 'Nombre original no proporcionado.'})

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            salas_sheet = sheet.worksheet('Salas')
            salas_records = salas_sheet.get_all_records()

            # Encontrar la fila de la sala original
            row_number = None
            for idx, record in enumerate(salas_records, start=2):  # start=2 porque la primera fila son encabezados
                if record.get('Nombre', '').strip().lower() == original_nombre.strip().lower():
                    row_number = idx
                    break

            if not row_number:
                return JsonResponse({'status': 'error', 'message': 'Sala no encontrada.'})

            # Actualizar los campos
            salas_sheet.update_cell(row_number, 1, nombre)   # Nombre
            salas_sheet.update_cell(row_number, 2, cbaja)    # CBaja
            salas_sheet.update_cell(row_number, 3, calta)    # CAlta

            # Si el nombre de la sala cambia, renombrar la hoja correspondiente
            if nombre.lower() != original_nombre.lower():
                try:
                    target_sheet = sheet.worksheet(original_nombre)
                    sheet.duplicate_sheet(source_sheet_id=target_sheet.id, new_sheet_name=nombre)
                    sheet.del_worksheet(target_sheet)
                except Exception as e:
                    print(f'Error al renombrar la hoja: {e}')
                    return JsonResponse({'status': 'error', 'message': 'Error al renombrar la hoja de la sala.'})

            return JsonResponse({'status': 'success', 'message': 'Sala actualizada exitosamente.'})

        except Exception as e:
            print(f'Error al editar sala: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error al editar la sala.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@csrf_exempt
def delete_sala(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')

            if not nombre:
                return JsonResponse({'status': 'error', 'message': 'Nombre de sala no proporcionado.'})

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            salas_sheet = sheet.worksheet('Salas')
            salas_records = salas_sheet.get_all_records()

            # Encontrar la fila de la sala
            row_number = None
            for idx, record in enumerate(salas_records, start=2):  # start=2 porque la primera fila son encabezados
                if record.get('Nombre', '').strip().lower() == nombre.strip().lower():
                    row_number = idx
                    break

            if not row_number:
                return JsonResponse({'status': 'error', 'message': 'Sala no encontrada.'})

            # Eliminar la fila
            salas_sheet.delete_rows(row_number)

            # Eliminar la hoja correspondiente a la Sala
            try:
                target_sheet = sheet.worksheet(nombre)
                sheet.del_worksheet(target_sheet)
            except Exception as e:
                print(f'Error al eliminar la hoja de la sala: {e}')
                # No retornamos un error aquí para no interrumpir el flujo principal

            return JsonResponse({'status': 'success', 'message': 'Sala eliminada exitosamente.'})

        except Exception as e:
            print(f'Error al eliminar sala: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error al eliminar la sala.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@csrf_exempt
def delete_all_salas(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            salas_sheet = sheet.worksheet('Salas')

            # Obtener todas las filas excepto la primera (encabezados)
            all_rows = salas_sheet.get_all_values()
            if len(all_rows) <= 1:
                return JsonResponse({'status': 'error', 'message': 'No hay salas para eliminar.'})

            # Eliminar todas las filas excepto la primera
            salas_sheet.batch_clear(['A2:C'])  # Asumiendo que hay 3 columnas: A-C

            # Eliminar todas las hojas de Salas excepto la hoja principal "Salas"
            worksheets = sheet.worksheets()
            for ws in worksheets:
                if ws.title != 'Salas':
                    sheet.del_worksheet(ws)

            return JsonResponse({'status': 'success', 'message': 'Todas las salas han sido eliminadas exitosamente.'})

        except Exception as e:
            print(f'Error al eliminar todas las salas: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error al eliminar todas las salas.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})

def manage_salas(request):
    try:
        client = connect_to_sheets()
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
        salas_sheet = sheet.worksheet('Salas')  # Asegúrate de que esta hoja exista
        salas_records = salas_sheet.get_all_records()

        # Preparar la lista de salas
        salas = []
        for record in salas_records:
            sala = {
                'nombre': record.get('Nombre', ''),
                'cbaja': record.get('CBaja', ''),
                'calta': record.get('CAlta', ''),
            }
            salas.append(sala)

        context = {
            'salas': salas,
        }

        return render(request, 'manage_salas.html', context)

    except Exception as e:
        print(f'Error al cargar salas: {e}')
        return render(request, 'manage_salas.html', {'salas': [], 'error': 'Error al cargar las salas.'})


@csrf_exempt
def add_sala(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            cbaja = data.get('cbaja')
            calta = data.get('calta')

            if not nombre or not cbaja or not calta:
                return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios.'})

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            salas_sheet = sheet.worksheet('Salas')

            # Verificar si ya existe una hoja con el mismo nombre
            try:
                existing_sheet = sheet.worksheet(nombre)
                return JsonResponse({'status': 'error', 'message': f'Ya existe una sala con el nombre "{nombre}".'})
            except:
                pass  # Si no existe, continuar

            # Añadir la nueva sala
            salas_sheet.append_row([nombre, cbaja, calta])

            # Crear una nueva hoja para la Sala con las columnas especificadas
            headers = [
                'Nombre', 'Marca', 'Modelo', 'Serie', 'Clasificación por riesgo',
                'Registro INVIMA', 'Lote', 'Vida útil', 'Voltaje (V)',
                'Corriente (A)', 'Potencia (W)', 'Kwh',
                'Consumibles (Desechables)', 'Accesorios (No desechables)'
            ]

            # Crear la nueva hoja
            new_sheet = sheet.add_worksheet(title=nombre, rows=100, cols=14)  # Puedes ajustar filas y columnas según necesidad
            new_sheet.append_row(headers)

            return JsonResponse({'status': 'success', 'message': 'Sala agregada exitosamente.'})

        except Exception as e:
            print(f'Error al agregar sala: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error al agregar la sala.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@csrf_exempt
def edit_sala(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            original_nombre = data.get('original_nombre')
            nombre = data.get('nombre')
            cbaja = data.get('cbaja')
            calta = data.get('calta')

            if not original_nombre:
                return JsonResponse({'status': 'error', 'message': 'Nombre original no proporcionado.'})

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            salas_sheet = sheet.worksheet('Salas')
            salas_records = salas_sheet.get_all_records()

            # Encontrar la fila de la sala original
            row_number = None
            for idx, record in enumerate(salas_records, start=2):  # start=2 porque la primera fila son encabezados
                if record.get('Nombre', '').strip().lower() == original_nombre.strip().lower():
                    row_number = idx
                    break

            if not row_number:
                return JsonResponse({'status': 'error', 'message': 'Sala no encontrada.'})

            # Actualizar los campos
            salas_sheet.update_cell(row_number, 1, nombre)   # Nombre
            salas_sheet.update_cell(row_number, 2, cbaja)    # CBaja
            salas_sheet.update_cell(row_number, 3, calta)    # CAlta

            # Si el nombre de la sala cambia, renombrar la hoja correspondiente
            if nombre.lower() != original_nombre.lower():
                try:
                    target_sheet = sheet.worksheet(original_nombre)
                    sheet.duplicate_sheet(source_sheet_id=target_sheet.id, new_sheet_name=nombre)
                    sheet.del_worksheet(target_sheet)
                except Exception as e:
                    print(f'Error al renombrar la hoja: {e}')
                    return JsonResponse({'status': 'error', 'message': 'Error al renombrar la hoja de la sala.'})

            return JsonResponse({'status': 'success', 'message': 'Sala actualizada exitosamente.'})

        except Exception as e:
            print(f'Error al editar sala: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error al editar la sala.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@csrf_exempt
def delete_sala(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')

            if not nombre:
                return JsonResponse({'status': 'error', 'message': 'Nombre de sala no proporcionado.'})

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            salas_sheet = sheet.worksheet('Salas')
            salas_records = salas_sheet.get_all_records()

            # Encontrar la fila de la sala
            row_number = None
            for idx, record in enumerate(salas_records, start=2):  # start=2 porque la primera fila son encabezados
                if record.get('Nombre', '').strip().lower() == nombre.strip().lower():
                    row_number = idx
                    break

            if not row_number:
                return JsonResponse({'status': 'error', 'message': 'Sala no encontrada.'})

            # Eliminar la fila
            salas_sheet.delete_rows(row_number)

            # Eliminar la hoja correspondiente a la Sala
            try:
                target_sheet = sheet.worksheet(nombre)
                sheet.del_worksheet(target_sheet)
            except Exception as e:
                print(f'Error al eliminar la hoja de la sala: {e}')
                # No retornamos un error aquí para no interrumpir el flujo principal

            return JsonResponse({'status': 'success', 'message': 'Sala eliminada exitosamente.'})

        except Exception as e:
            print(f'Error al eliminar sala: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error al eliminar la sala.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@csrf_exempt
def delete_all_salas(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            salas_sheet = sheet.worksheet('Salas')

            # Obtener todas las filas excepto la primera (encabezados)
            all_rows = salas_sheet.get_all_values()
            if len(all_rows) <= 1:
                return JsonResponse({'status': 'error', 'message': 'No hay salas para eliminar.'})

            # Eliminar todas las filas excepto la primera
            salas_sheet.batch_clear(['A2:C'])  # Asumiendo que hay 3 columnas: A-C

            # Eliminar todas las hojas de Salas excepto la hoja principal "Salas"
            worksheets = sheet.worksheets()
            for ws in worksheets:
                if ws.title != 'Salas':
                    sheet.del_worksheet(ws)

            return JsonResponse({'status': 'success', 'message': 'Todas las salas han sido eliminadas exitosamente.'})

        except Exception as e:
            print(f'Error al eliminar todas las salas: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error al eliminar todas las salas.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})



logger = logging.getLogger(__name__)

def manage_equipos(request):
    """
    Vista para renderizar la página de gestión de equipos biomédicos.
    Obtiene la lista de Salas desde Google Sheets para llenar los checkboxes en el frontend.
    """
    try:
        client = connect_to_sheets()
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
        
        # Obtener la hoja 'Salas'
        try:
            salas_sheet = sheet.worksheet('Salas')
            salas_records = salas_sheet.get_all_records()
            logger.info(f'Salas obtenidas: {len(salas_records)} registros.')
        except Exception as e:
            logger.error(f'Error al acceder a la hoja "Salas": {e}', exc_info=True)
            salas_records = []
        
        # Preparar la lista de Salas
        salas = []
        for record in salas_records:
            nombre_sala = record.get('Nombre', '').strip()
            if nombre_sala:
                salas.append(nombre_sala)
        
        logger.info(f'Lista de Salas: {salas}')
        
        context = {
            'salas': salas,
        }
        
        return render(request, 'manage_equipos.html', context)
    
    except Exception as e:
        logger.error(f'Error general al cargar equipos: {e}', exc_info=True)
        return render(request, 'manage_equipos.html', {'salas': [], 'error': 'Error al cargar los equipos.'})

@csrf_exempt
def get_equipos_by_sala(request):
    """
    Vista para obtener equipos biomédicos asignados a una Sala específica.
    Recibe el nombre de la Sala y retorna una lista de equipos.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            sala = data.get('sala')

            if not sala:
                logger.warning('No se proporcionó la Sala en la solicitud.')
                return JsonResponse({'status': 'error', 'message': 'No se proporcionó la Sala.'})

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')

            # Intentar acceder a la hoja específica de la Sala
            try:
                sala_sheet = sheet.worksheet(sala)
                equipos_records = sala_sheet.get_all_records()
                logger.info(f'Equipos obtenidos de la hoja "{sala}": {len(equipos_records)} registros.')
            except gspread.exceptions.WorksheetNotFound:
                logger.error(f'La hoja "{sala}" no existe en Google Sheets.')
                return JsonResponse({'status': 'error', 'message': f'La hoja "{sala}" no existe.'})
            except Exception as e:
                logger.error(f'Error al acceder a la hoja "{sala}": {e}', exc_info=True)
                return JsonResponse({'status': 'error', 'message': 'Error al acceder a la hoja de la Sala.'})

            # Preparar la lista de Equipos
            equipos_filtrados = []
            for record in equipos_records:
                equipo = {
                    'nombre': record.get('Nombre', ''),
                    'marca': record.get('Marca', ''),
                    'modelo': record.get('Modelo', ''),
                    'serie': record.get('Serie', ''),
                    'clasificacion_riesgo': record.get('Clasificación por riesgo', ''),
                    'registro_invima': record.get('Registro INVIMA', ''),
                    'lote': record.get('Lote', ''),
                    'vida_util': record.get('Vida útil', ''),
                    'voltaje': record.get('Voltaje (V)', ''),
                    'corriente': record.get('Corriente (A)', ''),
                    'potencia': record.get('Potencia (W)', ''),
                    'kwh': record.get('Kwh', ''),
                    'consumibles': record.get('Consumibles (Desechables)', ''),
                    'accesorios': record.get('Accesorios (No desechables)', ''),
                }
                equipos_filtrados.append(equipo)

            logger.info(f'Equipos filtrados para la Sala "{sala}": {len(equipos_filtrados)} registros.')

            return JsonResponse({'status': 'success', 'equipos': equipos_filtrados})

        except json.JSONDecodeError:
            logger.error('La solicitud no contiene un JSON válido.', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'La solicitud no contiene un JSON válido.'})
        except Exception as e:
            logger.error(f'Error inesperado al obtener equipos por sala: {e}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Error al obtener los equipos.'})
    else:
        logger.warning('Método no permitido para la vista get_equipos_by_sala.')
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})

@csrf_exempt
def add_equipo(request):
    """
    Vista para agregar un nuevo equipo biomédico a las Salas seleccionadas y almacenar información de residuos.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            marca = data.get('marca')
            modelo = data.get('modelo')
            serie = data.get('serie')
            clasificacion_riesgo = data.get('clasificacion_riesgo')
            registro_invima = data.get('registro_invima')
            lote = data.get('lote')
            vida_util = data.get('vida_util')
            voltaje = data.get('voltaje')
            corriente = data.get('corriente')
            potencia = data.get('potencia')
            kwh = data.get('kwh')
            consumibles = data.get('consumibles')
            accesorios = data.get('accesorios')
            salas = data.get('salas')  # Lista de Salas seleccionadas
            consumibles_dia = data.get('consumibles_dia')  # Nuevo Campo
            peso_kg = data.get('peso_kg')  # Nuevo Campo
            clasificacion = data.get('clasificacion')  # Nuevo Campo

            # Validaciones de campos obligatorios
            if not nombre or not marca or not modelo or not serie or not clasificacion_riesgo or not registro_invima \
               or not lote or not vida_util or not voltaje or not corriente or not potencia or not kwh \
               or not consumibles or not accesorios or not consumibles_dia or not peso_kg or not clasificacion:
                return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios.'})

            if not salas:
                return JsonResponse({'status': 'error', 'message': 'Por favor, selecciona al menos una Sala.'})

            # Convertir la lista de salas en una cadena separada por comas (opcional)
            salas_str = ', '.join(salas)

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')

            # Verificar si ya existe un equipo con el mismo nombre en alguna de las Salas seleccionadas
            existing_salas = []
            for sala in salas:
                try:
                    sala_sheet = sheet.worksheet(sala)
                    registros = sala_sheet.get_all_records()
                    for record in registros:
                        if record.get('Nombre', '').strip().lower() == nombre.strip().lower():
                            existing_salas.append(sala)
                            break  # Ya existe en esta Sala, no es necesario seguir buscando en esta hoja
                except gspread.exceptions.WorksheetNotFound:
                    logger.error(f'La hoja "{sala}" no existe en Google Sheets.')
                    return JsonResponse({'status': 'error', 'message': f'La hoja "{sala}" no existe.'})

            if existing_salas:
                return JsonResponse({'status': 'error', 'message': f'Ya existe un equipo con el nombre "{nombre}" en las Salas: {", ".join(existing_salas)}.'})

            # Añadir el nuevo equipo a cada Sala seleccionada
            for sala in salas:
                try:
                    sala_sheet = sheet.worksheet(sala)
                    sala_sheet.append_row([
                        nombre, marca, modelo, serie, clasificacion_riesgo,
                        registro_invima, lote, vida_util, voltaje,
                        corriente, potencia, kwh, consumibles,
                        accesorios, salas_str
                    ])
                except Exception as e:
                    logger.error(f'Error al añadir equipo a la hoja "{sala}": {e}', exc_info=True)
                    return JsonResponse({'status': 'error', 'message': f'Error al añadir el equipo a la Sala "{sala}".'})

            # Añadir información de Residuos en la hoja 'Residuos'
            try:
                residuos_sheet = sheet.worksheet('Residuos')
            except gspread.exceptions.WorksheetNotFound:
                # Si la hoja 'Residuos' no existe, crearla
                residuos_sheet = sheet.add_worksheet(title='Residuos', rows="100", cols="4")
                # Añadir encabezados
                residuos_sheet.append_row(['Equipo', 'ConsumiblesDia', 'Peso(kg)', 'Clasificacion'])

            residuos_sheet.append_row([
                nombre, consumibles_dia, peso_kg, clasificacion
            ])

            logger.info(f'Equipo "{nombre}" agregado exitosamente a las Salas: {", ".join(salas)} y registrado en Residuos.')

            return JsonResponse({'status': 'success', 'message': 'Equipo biomédico agregado exitosamente.'})

        except Exception as e:
            logger.error(f'Error al agregar equipo: {e}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Error al agregar el equipo biomédico.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})

@csrf_exempt
def edit_equipo(request):
    """
    Vista para editar un equipo biomédico existente.
    Permite asignar el equipo a múltiples Salas.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Cargar datos del cuerpo de la solicitud
            data = json.loads(request.body)
            original_nombre = data.get('original_nombre')
            nombre = data.get('nombre')
            marca = data.get('marca')
            modelo = data.get('modelo')
            serie = data.get('serie')
            clasificacion_riesgo = data.get('clasificacion_riesgo')
            registro_invima = data.get('registro_invima')
            lote = data.get('lote')
            vida_util = data.get('vida_util')
            voltaje = data.get('voltaje')
            corriente = data.get('corriente')
            potencia = data.get('potencia')
            kwh = data.get('kwh')
            consumibles = data.get('consumibles')
            accesorios = data.get('accesorios')
            salas = data.get('salas')  # Lista de Salas seleccionadas

            # Validaciones de campos obligatorios
            if not original_nombre:
                return JsonResponse({'status': 'error', 'message': 'Nombre original no proporcionado.'})

            if not nombre or not marca or not modelo or not serie or not clasificacion_riesgo or not registro_invima \
               or not lote or not vida_util or not voltaje or not corriente or not potencia or not kwh \
               or not consumibles or not accesorios:
                return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios.'})

            if not salas:
                return JsonResponse({'status': 'error', 'message': 'Por favor, selecciona al menos una Sala.'})

            # Convertir la lista de Salas en una cadena separada por comas
            salas_str = ', '.join(salas)

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')

            # Obtener la lista de todas las Salas desde la hoja 'Salas'
            try:
                salas_sheet = sheet.worksheet('Salas')
                salas_records = salas_sheet.get_all_records()
                all_salas = [record.get('Nombre', '').strip() for record in salas_records if record.get('Nombre', '').strip()]
                logger.info(f'Lista de Salas: {all_salas}')
            except gspread.exceptions.WorksheetNotFound:
                logger.error('La hoja "Salas" no existe en Google Sheets.')
                return JsonResponse({'status': 'error', 'message': 'La hoja "Salas" no existe.'})
            except Exception as e:
                logger.error(f'Error al acceder a la hoja "Salas": {e}', exc_info=True)
                return JsonResponse({'status': 'error', 'message': 'Error al acceder a la hoja "Salas".'})

            # Verificar si el nuevo nombre ya existe en las Salas seleccionadas (excluyendo el equipo actual)
            if nombre.strip().lower() != original_nombre.strip().lower():
                existing_salas = []
                for sala in salas:
                    try:
                        sala_sheet = sheet.worksheet(sala)
                        equipos_records = sala_sheet.get_all_records()
                        for record in equipos_records:
                            if record.get('Nombre', '').strip().lower() == nombre.strip().lower():
                                existing_salas.append(sala)
                                break  # Ya existe en esta Sala
                    except gspread.exceptions.WorksheetNotFound:
                        logger.error(f'La hoja "{sala}" no existe en Google Sheets.')
                        return JsonResponse({'status': 'error', 'message': f'La hoja "{sala}" no existe.'})
                    except Exception as e:
                        logger.error(f'Error al verificar duplicados en la Sala "{sala}": {e}', exc_info=True)
                        return JsonResponse({'status': 'error', 'message': f'Error al verificar duplicados en la Sala "{sala}".'})

                if existing_salas:
                    return JsonResponse({'status': 'error', 'message': f'Ya existe un equipo con el nombre "{nombre}" en la Sala(s): {", ".join(existing_salas)}.'})

            # Iterar sobre todas las Salas para actualizar o eliminar el Equipo
            for sala in all_salas:
                try:
                    sala_sheet = sheet.worksheet(sala)
                    equipos_records = sala_sheet.get_all_records()

                    # Buscar el Equipo por 'original_nombre'
                    row_number = None
                    for idx, record in enumerate(equipos_records, start=2):  # start=2 porque la primera fila son encabezados
                        if record.get('Nombre', '').strip().lower() == original_nombre.strip().lower():
                            row_number = idx
                            break

                    if sala in salas:
                        # Sala está seleccionada, añadir o actualizar el Equipo
                        if row_number:
                            # Equipo ya existe en esta Sala, actualizar sus campos
                            sala_sheet.update_cell(row_number, 1, nombre)               # Nombre
                            sala_sheet.update_cell(row_number, 2, marca)                # Marca
                            sala_sheet.update_cell(row_number, 3, modelo)               # Modelo
                            sala_sheet.update_cell(row_number, 4, serie)                # Serie
                            sala_sheet.update_cell(row_number, 5, clasificacion_riesgo)  # Clasificación por riesgo
                            sala_sheet.update_cell(row_number, 6, registro_invima)       # Registro INVIMA
                            sala_sheet.update_cell(row_number, 7, lote)                 # Lote
                            sala_sheet.update_cell(row_number, 8, vida_util)            # Vida útil
                            sala_sheet.update_cell(row_number, 9, voltaje)              # Voltaje (V)
                            sala_sheet.update_cell(row_number, 10, corriente)           # Corriente (A)
                            sala_sheet.update_cell(row_number, 11, potencia)            # Potencia (W)
                            sala_sheet.update_cell(row_number, 12, kwh)                 # Kwh
                            sala_sheet.update_cell(row_number, 13, consumibles)         # Consumibles (Desechables)
                            sala_sheet.update_cell(row_number, 14, accesorios)          # Accesorios (No desechables)
                            sala_sheet.update_cell(row_number, 15, salas_str)           # Salas
                            logger.info(f'Equipo "{original_nombre}" actualizado en la Sala "{sala}".')
                        else:
                            # Equipo no existe en esta Sala, añadirlo
                            sala_sheet.append_row([
                                nombre, marca, modelo, serie, clasificacion_riesgo,
                                registro_invima, lote, vida_util, voltaje,
                                corriente, potencia, kwh, consumibles,
                                accesorios, salas_str
                            ])
                            logger.info(f'Equipo "{nombre}" añadido a la Sala "{sala}".')
                    else:
                        # Sala no está seleccionada, eliminar el Equipo si existe
                        if row_number:
                            sala_sheet.delete_row(row_number)
                            logger.info(f'Equipo "{original_nombre}" eliminado de la Sala "{sala}".')
                except gspread.exceptions.WorksheetNotFound:
                    logger.error(f'La hoja "{sala}" no existe en Google Sheets.')
                    return JsonResponse({'status': 'error', 'message': f'La hoja "{sala}" no existe.'})
                except Exception as e:
                    logger.error(f'Error al procesar la Sala "{sala}": {e}', exc_info=True)
                    return JsonResponse({'status': 'error', 'message': f'Error al procesar la Sala "{sala}".'})

            logger.info(f'Equipo "{original_nombre}" actualizado a "{nombre}" exitosamente.')

            return JsonResponse({'status': 'success', 'message': 'Equipo biomédico actualizado exitosamente.'})

        except Exception as e:
            logger.error(f'Error al editar equipo: {e}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Error al editar el equipo biomédico.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})

@csrf_exempt
def delete_equipo(request):
    """
    Vista para eliminar un equipo biomédico de una Sala específica.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Cargar datos del cuerpo de la solicitud
            data = json.loads(request.body)
            nombre = data.get('nombre')
            sala = data.get('sala')

            # Validación de campos obligatorios
            if not nombre:
                return JsonResponse({'status': 'error', 'message': 'Nombre de equipo biomédico no proporcionado.'})

            if not sala:
                return JsonResponse({'status': 'error', 'message': 'Sala no proporcionada.'})

            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')

            # Verificar si la Sala existe
            try:
                sala_sheet = sheet.worksheet(sala)
            except gspread.exceptions.WorksheetNotFound:
                logger.error(f'La hoja "{sala}" no existe en Google Sheets.')
                return JsonResponse({'status': 'error', 'message': f'La hoja "{sala}" no existe.'})

            # Buscar el Equipo por 'nombre' en la Sala específica
            equipos_records = sala_sheet.get_all_records()
            row_number = None
            for idx, record in enumerate(equipos_records, start=2):  # start=2 porque la primera fila son encabezados
                if record.get('Nombre', '').strip().lower() == nombre.strip().lower():
                    row_number = idx
                    break

            if row_number:
                # Eliminar la fila del Equipo
                sala_sheet.delete_row(row_number)
                logger.info(f'Equipo "{nombre}" eliminado exitosamente de la Sala "{sala}".')
                return JsonResponse({'status': 'success', 'message': f'Equipo biomédico eliminado exitosamente de la Sala "{sala}".'})
            else:
                logger.warning(f'Equipo "{nombre}" no encontrado en la Sala "{sala}".')
                return JsonResponse({'status': 'error', 'message': f'Equipo biomédico "{nombre}" no encontrado en la Sala "{sala}".'})

        except json.JSONDecodeError:
            logger.error('La solicitud no contiene un JSON válido.', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'La solicitud no contiene un JSON válido.'})
        except Exception as e:
            logger.error(f'Error inesperado al eliminar equipo de Sala: {e}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Error al eliminar el equipo biomédico de la Sala.'})
    else:
        logger.warning('Método no permitido para la vista delete_equipo.')
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})

@csrf_exempt
def delete_all_equipos(request):
    """
    Vista para eliminar todos los equipos biomédicos de todas las Salas.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')

            # Obtener la lista de todas las Salas desde la hoja 'Salas'
            try:
                salas_sheet = sheet.worksheet('Salas')
                salas_records = salas_sheet.get_all_records()
                all_salas = [record.get('Nombre', '').strip() for record in salas_records if record.get('Nombre', '').strip()]
                logger.info(f'Lista de Salas: {all_salas}')
            except gspread.exceptions.WorksheetNotFound:
                logger.error('La hoja "Salas" no existe en Google Sheets.')
                return JsonResponse({'status': 'error', 'message': 'La hoja "Salas" no existe.'})
            except Exception as e:
                logger.error(f'Error al acceder a la hoja "Salas": {e}', exc_info=True)
                return JsonResponse({'status': 'error', 'message': 'Error al acceder a la hoja "Salas".'})

            # Iterar sobre todas las Salas para eliminar todos los Equipos
            equipos_eliminados = []
            for sala in all_salas:
                try:
                    sala_sheet = sheet.worksheet(sala)
                    # Obtener todas las filas excepto la primera (encabezados)
                    all_rows = sala_sheet.get_all_values()
                    if len(all_rows) <= 1:
                        logger.info(f'No hay equipos para eliminar en la Sala "{sala}".')
                        continue  # No hay equipos para eliminar en esta Sala

                    # Eliminar todas las filas excepto la primera
                    # Google Sheets API no permite eliminar un rango completo de filas directamente,
                    # así que eliminaremos filas una por una desde la última hacia la segunda.
                    total_filas = len(all_rows)
                    for row in range(total_filas, 1, -1):  # Desde la última fila hasta la segunda
                        sala_sheet.delete_row(row)

                    equipos_eliminados.append(sala)
                    logger.info(f'Todos los equipos eliminados de la Sala "{sala}".')
                except gspread.exceptions.WorksheetNotFound:
                    logger.error(f'La hoja "{sala}" no existe en Google Sheets.')
                    return JsonResponse({'status': 'error', 'message': f'La hoja "{sala}" no existe.'})
                except Exception as e:
                    logger.error(f'Error al procesar la Sala "{sala}": {e}', exc_info=True)
                    return JsonResponse({'status': 'error', 'message': f'Error al procesar la Sala "{sala}".'})

            if not equipos_eliminados:
                return JsonResponse({'status': 'error', 'message': 'No hay equipos biomédicos para eliminar en ninguna Sala.'})

            logger.info(f'Todos los equipos biomédicos han sido eliminados de las Salas: {", ".join(equipos_eliminados)}.')

            return JsonResponse({'status': 'success', 'message': f'Todos los equipos biomédicos han sido eliminados de las Salas: {", ".join(equipos_eliminados)}.'})

        except Exception as e:
            logger.error(f'Error al eliminar todos los equipos: {e}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Error al eliminar todos los equipos biomédicos.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})
    
@csrf_exempt
def manage_clasificacion_residuos(request):
    """
    Vista para renderizar la página de gestión de Clasificación de Residuos.
    """
    try:
        client = connect_to_sheets()
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
        
        # Obtener la hoja 'ClasificacionResiduos'
        try:
            residuos_sheet = sheet.worksheet('ClasificacionResiduos')
            residuos_records = residuos_sheet.get_all_records()
            logger.info(f'Residuos obtenidos: {len(residuos_records)} registros.')
        except gspread.exceptions.WorksheetNotFound:
            # Si la hoja no existe, crearla y añadir encabezados
            residuos_sheet = sheet.add_worksheet(title='ClasificacionResiduos', rows="100", cols="2")
            residuos_sheet.append_row(['Nombre', 'Clasificación'])
            residuos_records = []
            logger.info('Hoja "ClasificacionResiduos" creada y encabezados añadidos.')
        
        context = {
            'residuos': residuos_records,
        }
        
        return render(request, 'manage_clasificacion_residuos.html', context)
    
    except Exception as e:
        logger.error(f'Error al cargar ClasificacionResiduos: {e}', exc_info=True)
        return render(request, 'manage_clasificacion_residuos.html', {'residuos': [], 'error': 'Error al cargar la clasificación de residuos.'})


@csrf_exempt
def get_clasificacion_residuos(request):
    """
    Vista para obtener todas las clasificaciones de residuos.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            
            # Acceder a la hoja 'ClasificacionResiduos'
            try:
                residuos_sheet = sheet.worksheet('ClasificacionResiduos')
                residuos_records = residuos_sheet.get_all_records()
                logger.info(f'Clasificaciones de residuos obtenidas: {len(residuos_records)} registros.')
            except gspread.exceptions.WorksheetNotFound:
                logger.error('La hoja "ClasificacionResiduos" no existe en Google Sheets.')
                return JsonResponse({'status': 'error', 'message': 'La hoja "ClasificacionResiduos" no existe.'})
            
            # Preparar la lista de clasificaciones
            residuos = []
            for record in residuos_records:
                residuo = {
                    'nombre': record.get('Nombre', '').strip(),
                    'clasificacion': record.get('Clasificación', '').strip(),
                }
                residuos.append(residuo)
            
            return JsonResponse({'status': 'success', 'residuos': residuos})
        
        except json.JSONDecodeError:
            logger.error('La solicitud no contiene un JSON válido.', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'La solicitud no contiene un JSON válido.'})
        except Exception as e:
            logger.error(f'Error inesperado al obtener clasificaciones de residuos: {e}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Error al obtener las clasificaciones de residuos.'})
    else:
        logger.warning('Método no permitido para la vista get_clasificacion_residuos.')
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@csrf_exempt
def add_clasificacion_residuo(request):
    """
    Vista para agregar una nueva clasificación de residuo.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            clasificacion = data.get('clasificacion')
            
            # Validaciones de campos obligatorios
            if not nombre or not clasificacion:
                return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios.'})
            
            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            
            # Acceder a la hoja 'ClasificacionResiduos'
            try:
                residuos_sheet = sheet.worksheet('ClasificacionResiduos')
            except gspread.exceptions.WorksheetNotFound:
                # Si la hoja no existe, crearla y añadir encabezados
                residuos_sheet = sheet.add_worksheet(title='ClasificacionResiduos', rows="100", cols="2")
                residuos_sheet.append_row(['Nombre', 'Clasificación'])
                logger.info('Hoja "ClasificacionResiduos" creada y encabezados añadidos.')
            
            # Verificar si ya existe una clasificación con el mismo nombre
            residuos_records = residuos_sheet.get_all_records()
            for record in residuos_records:
                if record.get('Nombre', '').strip().lower() == nombre.strip().lower():
                    return JsonResponse({'status': 'error', 'message': f'Ya existe una clasificación con el nombre "{nombre}".'})
            
            # Añadir la nueva clasificación
            residuos_sheet.append_row([nombre.strip(), clasificacion.strip()])
            logger.info(f'Clasificación de residuo "{nombre}" añadida exitosamente.')
            
            return JsonResponse({'status': 'success', 'message': 'Clasificación de residuo añadida exitosamente.'})
        
        except Exception as e:
            logger.error(f'Error al agregar clasificación de residuo: {e}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Error al agregar la clasificación de residuo.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@csrf_exempt
def edit_clasificacion_residuo(request):
    """
    Vista para editar una clasificación de residuo existente.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            original_nombre = data.get('original_nombre')
            nombre = data.get('nombre')
            clasificacion = data.get('clasificacion')
            
            # Validaciones de campos obligatorios
            if not original_nombre or not nombre or not clasificacion:
                return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios.'})
            
            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            
            # Acceder a la hoja 'ClasificacionResiduos'
            try:
                residuos_sheet = sheet.worksheet('ClasificacionResiduos')
            except gspread.exceptions.WorksheetNotFound:
                logger.error('La hoja "ClasificacionResiduos" no existe en Google Sheets.')
                return JsonResponse({'status': 'error', 'message': 'La hoja "ClasificacionResiduos" no existe.'})
            
            # Obtener todas las filas
            all_records = residuos_sheet.get_all_records()
            row_number = None
            for idx, record in enumerate(all_records, start=2):  # start=2 porque la primera fila son encabezados
                if record.get('Nombre', '').strip().lower() == original_nombre.strip().lower():
                    row_number = idx
                    break
            
            if not row_number:
                return JsonResponse({'status': 'error', 'message': f'Clasificación con el nombre "{original_nombre}" no encontrada.'})
            
            # Verificar si el nuevo nombre ya existe (excluyendo el actual)
            for idx, record in enumerate(all_records, start=2):
                if record.get('Nombre', '').strip().lower() == nombre.strip().lower() and idx != row_number:
                    return JsonResponse({'status': 'error', 'message': f'Ya existe una clasificación con el nombre "{nombre}".'})
            
            # Actualizar la clasificación
            residuos_sheet.update_cell(row_number, 1, nombre.strip())
            residuos_sheet.update_cell(row_number, 2, clasificacion.strip())
            logger.info(f'Clasificación de residuo "{original_nombre}" actualizada a "{nombre}".')
            
            return JsonResponse({'status': 'success', 'message': 'Clasificación de residuo actualizada exitosamente.'})
        
        except Exception as e:
            logger.error(f'Error al editar clasificación de residuo: {e}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Error al editar la clasificación de residuo.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@csrf_exempt
def delete_clasificacion_residuo(request):
    """
    Vista para eliminar una clasificación de residuo específica.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            
            # Validación de campo obligatorio
            if not nombre:
                return JsonResponse({'status': 'error', 'message': 'Nombre de clasificación de residuo no proporcionado.'})
            
            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            
            # Acceder a la hoja 'ClasificacionResiduos'
            try:
                residuos_sheet = sheet.worksheet('ClasificacionResiduos')
            except gspread.exceptions.WorksheetNotFound:
                logger.error('La hoja "ClasificacionResiduos" no existe en Google Sheets.')
                return JsonResponse({'status': 'error', 'message': 'La hoja "ClasificacionResiduos" no existe.'})
            
            # Obtener todas las filas
            all_records = residuos_sheet.get_all_records()
            row_number = None
            for idx, record in enumerate(all_records, start=2):  # start=2 porque la primera fila son encabezados
                if record.get('Nombre', '').strip().lower() == nombre.strip().lower():
                    row_number = idx
                    break
            
            if not row_number:
                return JsonResponse({'status': 'error', 'message': f'Clasificación de residuo "{nombre}" no encontrada.'})
            
            # Eliminar la fila
            residuos_sheet.delete_row(row_number)
            logger.info(f'Clasificación de residuo "{nombre}" eliminada exitosamente.')
            
            return JsonResponse({'status': 'success', 'message': 'Clasificación de residuo eliminada exitosamente.'})
        
        except Exception as e:
            logger.error(f'Error al eliminar clasificación de residuo: {e}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Error al eliminar la clasificación de residuo.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@csrf_exempt
def delete_all_clasificacion_residuos(request):
    """
    Vista para eliminar todas las clasificaciones de residuos.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # Conectar con Google Sheets
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            
            # Acceder a la hoja 'ClasificacionResiduos'
            try:
                residuos_sheet = sheet.worksheet('ClasificacionResiduos')
            except gspread.exceptions.WorksheetNotFound:
                logger.error('La hoja "ClasificacionResiduos" no existe en Google Sheets.')
                return JsonResponse({'status': 'error', 'message': 'La hoja "ClasificacionResiduos" no existe.'})
            
            # Obtener todas las filas
            all_rows = residuos_sheet.get_all_values()
            if len(all_rows) <= 1:
                return JsonResponse({'status': 'error', 'message': 'No hay clasificaciones de residuos para eliminar.'})
            
            # Eliminar todas las filas excepto la primera (encabezados)
            total_filas = len(all_rows)
            for row in range(total_filas, 1, -1):  # Desde la última fila hasta la segunda
                residuos_sheet.delete_row(row)
            
            logger.info('Todas las clasificaciones de residuos han sido eliminadas exitosamente.')
            
            return JsonResponse({'status': 'success', 'message': 'Todas las clasificaciones de residuos han sido eliminadas.'})
        
        except Exception as e:
            logger.error(f'Error al eliminar todas las clasificaciones de residuos: {e}', exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Error al eliminar todas las clasificaciones de residuos.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})
    
def manage_pconsumo(request):
    try:
        client = connect_to_sheets()
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
        try:
            # Intentar acceder a la hoja 'PConsumo'
            pconsumo_sheet = sheet.worksheet("PConsumo")
            print(pconsumo_sheet)
            pconsumo_values = pconsumo_sheet.get_all_values()
            # Si no hay datos (menos de 2 filas), inicializamos con encabezados
            if len(pconsumo_values) < 2:
                pconsumo_sheet.append_row(["Baja", "Alta"])
                pconsumo_values = pconsumo_sheet.get_all_values()
            data = pconsumo_values[1]  # segunda fila
            pconsumo = {"baja": data[0], "alta": data[1]}
        except gspread.exceptions.WorksheetNotFound:
            # Si la hoja no existe, la creamos con encabezados
            pconsumo_sheet = sheet.add_worksheet(title="PConsumo", rows="2", cols="2")
            pconsumo_sheet.append_row(["Baja", "Alta"])
            pconsumo = {"baja": "", "alta": ""}
            logger.info('Hoja "PConsumo" creada y encabezados añadidos.')
        
        context = {"pconsumo": pconsumo}
        return render(request, "manage_pconsumo.html", context)
    except Exception as e:
        logger.error("Error al cargar PConsumo", exc_info=True)
        return render(request, "manage_pconsumo.html", {"error": "Error al cargar los datos de PConsumo"})

# Vista AJAX para actualizar los valores de PConsumo
@csrf_exempt
def update_pconsumo(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            data = json.loads(request.body)
            nueva_baja = data.get("baja")
            nueva_alta = data.get("alta")
            if nueva_baja is None or nueva_alta is None:
                return JsonResponse({"status": "error", "message": "Ambos valores son obligatorios."})
            client = connect_to_sheets()
            sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RNfUqVAu5dpEgPvuHoDBvt81SK0Nc_zxDFQpeprPhno/edit')
            try:
                pconsumo_sheet = sheet.worksheet("PConsumo")
            except gspread.exceptions.WorksheetNotFound:
                pconsumo_sheet = sheet.add_worksheet(title="PConsumo", rows="2", cols="2")
                pconsumo_sheet.append_row(["Baja", "Alta"])
            # Actualizar la fila 2: para cada columna usamos update() (el método update_cell ha quedado obsoleto en algunas versiones)
            pconsumo_sheet.update("A2", nueva_baja)
            pconsumo_sheet.update("B2", nueva_alta)
            return JsonResponse({"status": "success", "message": "Valores actualizados correctamente."})
        except Exception as e:
            logger.error("Error al actualizar PConsumo", exc_info=True)
            return JsonResponse({"status": "error", "message": "Error al actualizar los datos."})
    else:
        return JsonResponse({"status": "error", "message": "Método no permitido."})