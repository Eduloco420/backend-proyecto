CREATE OR REPLACE VIEW v_sucursal AS (
  SELECT
    s.id,
    s.nomSucursal,
    s.direccionSucursal,
    c.nomComuna,
    p.nomProvincia,
    r.nomRegion,
    ts.glosaTipoSucursal,
    s.activaSucursal
  FROM sucursal s
  JOIN comuna c ON c.id = s.comunaSucursal
  JOIN provincia p ON c.provincia = p.id
  JOIN region r ON r.id = p.region
  JOIN tipoSucursal ts ON ts.id = s.tipoSucursal
);

CREATE OR REPLACE VIEW v_sucursal_2 AS (
	SELECT 	s.id,
			nomSucursal,
			direccionSucursal,
			tipoSucursal,
			activaSucursal,
			comunaSucursal as 'Comuna',
			p.id as 'Provincia',
			r.id as 'region'
	FROM sucursal s
	INNER JOIN comuna c
	ON (s.comunaSucursal = c.id)
	INNER JOIN provincia p
	ON (c.provincia = p.id)
	INNER JOIN region r
	ON (p.region = r.id)
);

CREATE OR REPLACE VIEW v_producto_lista AS (
  SELECT
    p.id AS idProducto,
    p.nomProducto,
    c.id AS idCategoria,
    p.marcaProducto AS idMarca,
    p.subCatProducto AS idSubCategoria,
    c.nomCategoria,
    sc.nomSubCategoria,
    m.nomMarca,
    vp.valorProducto AS valorOriginal,
    ROUND(vp.valorProducto * (1 - dp.porcDescuento / 100), 0) AS valorOferta,
    i.imagen,
    p.despachoDomicilio,
    p.retiroSucursal,
    (
      SELECT COUNT(*)
      FROM opcionProducto op
      WHERE op.producto = p.id AND op.opcionActiva = 1
    ) AS cantidadOpciones
  FROM productos p
  JOIN valorProducto vp ON p.id = vp.producto
  JOIN subCategoria sc ON p.subCatProducto = sc.id
  JOIN categoria c ON sc.categoria = c.id
  JOIN marca m ON p.marcaProducto = m.id
  LEFT JOIN imagenProducto i ON p.id = i.producto
  LEFT JOIN descuentoProducto dp ON dp.id = (
    SELECT dp2.id
    FROM descuentoProducto dp2
    WHERE dp2.producto = p.id
      AND dp2.fecInicVigDescuento <= NOW()
      AND dp2.fecTermVigDescuento >= NOW()
    ORDER BY dp2.fecInicVigDescuento DESC
    LIMIT 1
  )
  WHERE p.productoActive = 1
    AND vp.fecInicVigValor = (
      SELECT MAX(vp2.fecInicVigValor)
      FROM valorProducto vp2
      WHERE vp2.producto = p.id AND vp2.fecInicVigValor <= NOW()
    )
    AND (
      i.id = (
        SELECT MIN(id)
        FROM imagenProducto i2
        WHERE i2.producto = p.id
      ) OR i.id IS NULL
    )
);

CREATE OR REPLACE VIEW v_detalle_producto_1 AS (
  SELECT
    p.id,
    p.nomProducto,
    p.descProducto,
    p.subCatProducto,
    sc.nomSubCategoria,
    sc.categoria,
    c.nomCategoria,
    p.marcaProducto,
    m.nomMarca,
    p.despachoDomicilio,
    p.retiroSucursal,
    p.opcion
  FROM productos p
  JOIN subCategoria sc ON p.subCatProducto = sc.id
  JOIN categoria c ON sc.categoria = c.id
  JOIN marca m ON p.marcaProducto = m.id
);

CREATE OR REPLACE VIEW v_detalle_producto_2 AS (
  SELECT
    producto,
    nombreEspecificacion,
    valorEspecificacion
  FROM especificacionProducto
);

CREATE OR REPLACE VIEW v_detalle_producto_3 AS (
  SELECT
    op.id,
    op.producto,
    op.glosaOpcion,
    SUM(i.stock) AS stockTotal
  FROM opcionProducto op
  JOIN inventario i ON op.id = i.producto
  GROUP BY op.id, op.producto, op.glosaOpcion, op.opcionActiva
);

CREATE OR REPLACE VIEW v_subcategorias AS (
  SELECT
    sc.id,
    sc.nomSubCategoria,
    sc.categoria,
    c.nomCategoria
  FROM subCategoria sc
  JOIN categoria c ON sc.categoria = c.id
);

CREATE OR REPLACE VIEW v_ventas AS (
  SELECT
    v.id,
    COALESCE(u.rutUsuario, ci.rutClienteInv) AS rutCliente,
    COALESCE(CONCAT(u.nomUsuario, ' ', u.apeUsuario), CONCAT(ci.nomClienteInv, ' ', ci.apeClienteInv)) AS nombreCliente,
    COALESCE(u.mailUsuario, ci.mailClienteInv) AS mailCliente,
    v.fecVenta,
    CASE 
        WHEN d.id IS NOT NULL THEN 'Despacho'
        WHEN r.id IS NOT NULL THEN 'Retiro'
        ELSE 'Sin entrega registrada'
    END AS tipoEntrega,
    v.estadoVenta,
    ev.glosaEstadoVta
  FROM venta v
  LEFT JOIN despacho d ON d.venta = v.id
  LEFT JOIN retiro r ON r.venta = v.id
  LEFT JOIN usuario u ON v.cliente = u.id
  LEFT JOIN clienteInvitado ci ON v.clienteInvitado = ci.id
  LEFT JOIN estadoVenta ev ON v.estadoVenta = ev.id
);

CREATE OR REPLACE VIEW v_pagos AS
    SELECT 
        p.id AS id,
        p.venta AS venta,
        CONCAT(REPEAT('*', 11),
		RIGHT(p.nroTarjeta, 5)) AS 'nro Tarjeta',
        p.montoPago AS montoPago,
        p.estadoPago AS estadoPago,
        ep.glosaEstadoPago AS glosaEstadoPago
    FROM
        pago p
        LEFT JOIN estadoPago ep 
        ON (p.estadoPago = ep.id);
        
CREATE OR REPLACE VIEW v_detalle_venta AS
	SELECT 
    dv.venta AS idVenta,
    dv.id AS idDetalle,
    op.id AS idOpcion,
    p.nomProducto,
    m.nomMarca,
    op.glosaOpcion,
    dv.cantidad,
    vp.valorProducto,
    IFNULL(dp.porcDescuento, 0) AS porcDescuento,
    ROUND(dv.cantidad * vp.valorProducto * (1 - IFNULL(dp.porcDescuento, 0)/100), 2) AS totalItem
FROM detalleVenta dv
INNER JOIN opcionProducto op 
    ON dv.opcionProducto = op.id
INNER JOIN productos p 
    ON op.producto = p.id
INNER JOIN marca m
    ON p.marcaProducto = m.id
INNER JOIN venta v 
    ON dv.venta = v.id
INNER JOIN valorProducto vp
    ON vp.producto = p.id
   AND vp.fecInicVigValor = (
       SELECT MAX(vp2.fecInicVigValor)
       FROM valorProducto vp2
       WHERE vp2.producto = p.id
         AND vp2.fecInicVigValor <= v.fecVenta
   )
LEFT JOIN descuentoProducto dp
    ON dp.producto = p.id
   AND v.fecVenta BETWEEN dp.fecInicVigDescuento AND dp.fecTermVigDescuento;

    
CREATE OR REPLACE VIEW v_forma_entrega AS
	SELECT 
		v.id AS venta_id,
		CASE 
			WHEN d.id IS NOT NULL THEN 'Despacho'
			WHEN r.id IS NOT NULL THEN 'Retiro'
			ELSE 'Sin entrega registrada'
		END AS tipo_entrega
	FROM venta v
	LEFT JOIN despacho d ON d.venta = v.id
	LEFT JOIN retiro r ON r.venta = v.id;   
    
CREATE OR REPLACE VIEW v_detalle_producto AS
	SELECT 	p.id,
			p.nomProducto,
			p.descProducto,
			p.subCatProducto,
			sc.nomSubCategoria,
			sc.categoria,
			c.nomCategoria,
			p.marcaProducto,
			m.nomMarca,
			p.opcion,
			p.productoActive,
			p.retiroSucursal,
			p.despachoDomicilio
	FROM productos p
	INNER JOIN marca m
	ON (p.marcaProducto = m.id)
	INNER JOIN subCategoria sc
	ON (p.subCatProducto = sc.id)
	INNER JOIN categoria c
	ON (sc.categoria = c.id);
    
CREATE OR REPLACE VIEW v_detalle_stock AS
	SELECT 	op.id,
			op.producto,
			op.glosaOpcion,
			op.opcionActiva,
			sum(i.stock) as cantidad,
			i.sucursal,
			s.nomSucursal
	FROM opcionProducto op
	INNER JOIN inventario i 
	ON (op.id = i.producto)
	INNER JOIN sucursal s 
	ON (i.sucursal = s.id)
	WHERE op.producto = 1
	GROUP BY 	op.id,
				op.producto,
				op.glosaOpcion,
				op.opcionActiva,
				i.sucursal;