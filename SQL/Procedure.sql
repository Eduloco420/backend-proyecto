DELIMITER $$

CREATE PROCEDURE sp_eliminar_producto(IN p_idProducto INT)
BEGIN
    DECLARE v_existeVenta INT DEFAULT 0;

    -- Verificar si el producto está en alguna venta
    SELECT COUNT(*) INTO v_existeVenta
    FROM detalleVenta
    WHERE opcionProducto in (SELECT id from opcionProducto where producto = p_idProducto);

    IF v_existeVenta > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No se puede eliminar el producto: tiene ventas asociadas.';
    ELSE
        DELETE FROM imagenProducto WHERE producto = p_idProducto;

        DELETE FROM especificacionProducto WHERE producto = p_idProducto;

        DELETE FROM productoFavorito WHERE producto = p_idProducto;

        DELETE FROM sucursalRetiro WHERE producto = p_idProducto;

        DELETE FROM descuentoProducto WHERE producto = p_idProducto;

        DELETE FROM valorProducto WHERE producto = p_idProducto;

        DELETE i FROM inventario i
        JOIN opcionProducto op ON i.producto = op.id
        WHERE op.producto = p_idProducto;

        DELETE FROM opcionProducto WHERE producto = p_idProducto;

        DELETE FROM productos WHERE id = p_idProducto;
    END IF;
END$$

DELIMITER ;
