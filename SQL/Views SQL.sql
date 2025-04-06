CREATE OR REPLACE VIEW v_sucursal AS (SELECT 	s.id, 
		s.nomSucursal, 
        s.direccionSucursal, 
        c.nomComuna, 
        p.nomProvincia, 
        r.nomRegion,
        ts.glosaTipoSucursal,
        activaSucursal 
FROM sucursal s, comuna c, provincia p, region r, tipoSucursal ts
WHERE 	c.id = s.comunaSucursal AND
		ts.id = s.tipoSucursal AND
		c.provincia = p.id AND
        r.id = p.region AND
        s.activaSucursal = 1);
        
CREATE OR REPLACE VIEW v_producto_lista AS (
	SELECT 	p.id AS idProducto,
		p.nomProducto,
        c.id as 'idCategoria',
		p.marcaProducto as 'idMarca',
		p.subCatProducto as 'idSubCategoria',
		c.nomCategoria,
		sc.nomSubCategoria,
		m.nomMarca,
		vp.valorProducto as 'valorOriginal',
        round((vp.valorProducto * (dp.porcDescuento / 100)),0) as 'valorOferta',
		i.imagen,
        p.despachoDomicilio,
        p.retiroSucursal
FROM productos p
	JOIN valorProducto vp ON p.id = vp.producto
	JOIN subCategoria sc ON p.subCatProducto = sc.id
	JOIN categoria c ON sc.categoria = c.id
	JOIN marca m ON p.marcaProducto = m.id
	LEFT JOIN imagenProducto i ON p.id = i.producto
    LEFT JOIN descuentoProducto dp ON dp.id =  (
			SELECT dp2.id
			FROM descuentoProducto dp2
            WHERE dp2.producto = p.id
            AND (dp2.fecInicVigDescuento <= NOW() 
            AND dp2.fecTermVigDescuento >= NOW())
            ORDER BY dp2.fecInicVigDescuento DESC
			LIMIT 1
		)
WHERE 	p.productoActive = 1 AND
		vp.fecInicVigValor = (
			SELECT MAX(vp2.fecInicVigValor)
			FROM valorProducto vp2
			WHERE vp2.producto = p.id AND vp2.fecInicVigValor <= now()
		) AND
		(i.id = (
			SELECT MIN(id)
            FROM imagenProducto i2
            WHERE i2.producto = p.id
        ) OR i.id IS NULL)
);