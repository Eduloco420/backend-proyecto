INSERT INTO rolusuario VALUES (1, 'Cliente');
INSERT INTO rolusuario VALUES (2, 'Administrador');

INSERT INTO tiposucursal VALUES 
(1, 'Bodega'),
(2, 'Tienda');

INSERT INTO tienda VALUES (1, 'Tienda Prueba', null, null, null, 'http://localhost:8080');

INSERT INTO estadoVenta VALUES 
('1','Pendiente'),
('2','Pagado'),
('3','Enviado'),
('4','Entregado'),
('5','Cancelado');

INSERT INTO estadoPago VALUES 
( '1','Pendiente Pago'),
( '2','Pagado'),
( '3','Rechazado'),
( '4','Devolución en Proceso');

INSERT INTO estadoDespacho VALUES
( '1','Pendiente Envío'),
( '2','Enviado'),
( '3','Pendiente confirmación Recepción'),
( '4','Recepción confirmada'),
( '5','Cancelado');

INSERT INTO estadoRetiro VALUES 
( '1','Pendiente confirmación'),
( '2','Listo para retirar'),
( '3','Entregado');