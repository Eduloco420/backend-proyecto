CREATE SCHEMA easycommerce;

USE easycommerce;

CREATE TABLE `tienda` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `nomTienda` varchar(100) NOT NULL,
  `facebookTienda` varchar(15),
  `instagramTienda` varchar(15),
  `xTienda` varchar(15),
  `dominioTienda` varchar(255)
);

CREATE TABLE `usuario` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `rutUsuario` varchar(10) UNIQUE NOT NULL,
  `nomUsuario` varchar(25) NOT NULL,
  `apeUsuario` varchar(25) NOT NULL,
  `mailUsuario` varchar(50) NOT NULL,
  `rolUsuario` int NOT NULL,
  `passUsuario` varchar(255) NOT NULL,
  `fecCreacionUsuario` datetime DEFAULT NOW(),
  `activeUsuario` boolean DEFAULT True
);

CREATE TABLE `region` (
  `id` int PRIMARY KEY,
  `nomRegion` varchar(50) NOT NULL,
  `abreviatura` varchar(4) NOT NULL,
  `capital` varchar(64) NOT NULL
);

CREATE TABLE `provincia` (
  `id` int PRIMARY KEY,
  `nomProvincia` varchar(50) NOT NULL,
  `region` int NOT NULL
);

CREATE TABLE `comuna` (
  `id` int PRIMARY KEY,
  `nomComuna` varchar(50) NOT NULL,
  `provincia` int
);

CREATE TABLE `rolUsuario` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `glosaRolUsuario` varchar(20) NOT NULL
);

CREATE TABLE `clienteInvitado` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `rutClienteInv` varchar(10) NOT NULL,
  `nomClienteInv` varchar(25) NOT NULL,
  `apeClienteInv` varchar(25) NOT NULL,
  `mailClienteInv` varchar(50) NOT NULL
);

CREATE TABLE `tipoSucursal` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `glosaTipoSucursal` varchar(20) NOT NULL
);

CREATE TABLE `sucursal` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `nomSucursal` varchar(100) NOT NULL,
  `direccionSucursal` varchar(200) NOT NULL,
  `comunaSucursal` int NOT NULL,
  `tipoSucursal` int NOT NULL,
  `activaSucursal` boolean DEFAULT True
);

CREATE TABLE `categoria` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `nomCategoria` varchar(40) NOT NULL
);

CREATE TABLE `subCategoria` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `nomSubCategoria` varchar(40) NOT NULL,
  `categoria` int NOT NULL
);

CREATE TABLE `productos` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `nomProducto` varchar(50) NOT NULL,
  `descProducto` varchar(1000),
  `subCatProducto` int,
  `marcaProducto` int NOT NULL,
  `opcion` varchar(20),
  `productoActive` boolean DEFAULT 1,
  `retiroSucursal` boolean NOT NULL,
  `despachoDomicilio` boolean NOT NULL
);

CREATE TABLE `valorProducto` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `producto` int NOT NULL,
  `valorProducto` float NOT NULL,
  `fecInicVigValor` datetime NOT NULL
);

CREATE TABLE `descuentoProducto` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `producto` int NOT NULL,
  `fecInicVigDescuento` datetime NOT NULL,
  `fecTermVigDescuento` datetime NOT NULL,
  `porcDescuento` float NOT NULL
);

CREATE TABLE `detalleVenta` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `venta` int NOT NULL,
  `producto` int NOT NULL
);

CREATE TABLE `estadoVenta` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `glosaEstadoVta` varchar(20) NOT NULL
);

CREATE TABLE `venta` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `cliente` int,
  `clienteInvitado` int,
  `fecVenta` datetime DEFAULT NOW(),
  `estadoVenta` int NOT NULL
);

CREATE TABLE `estadoDespacho` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `glosaEstadoDespacho` varchar(50) NOT NULL
);

CREATE TABLE `despacho` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `venta` int NOT NULL,
  `estadoDespacho` int NOT NULL,
  `codSeguimiento` varchar(20),
  `empresaDespacho` varchar(20),
  `enlaceSeguimiento` varchar(255),
  `fecDespacho` datetime,
  `fecEstimadaRecepcion` datetime,
  `calleDespacho` varchar(60),
  `numeroCalleDespacho` varchar(10),
  `comunaDespacho` int
);

CREATE TABLE `pago` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `venta` int NOT NULL,
  `nroTarjeta` varchar(16) NOT NULL,
  `fecVencTarjeta` varchar(5) NOT NULL,
  `cvv` int NOT NULL,
  `montoPago` float NOT NULL,
  `estadoPago` int NOT NULL
);

CREATE TABLE `sucursalRetiro` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `producto` int,
  `sucursal` int
);

CREATE TABLE `inventario` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `producto` int,
  `stock` int,
  `sucursal` int
);

CREATE TABLE `productoFavorito` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `producto` int,
  `usuario` int
);

CREATE TABLE `especificacionProducto` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `producto` int,
  `nombreEspecificacion` varchar(15),
  `valorEspecificacion` varchar(15)
);

CREATE TABLE `opcionProducto` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `producto` int,
  `glosaOpcion` varchar(25),
  `opcionActiva` boolean
);

CREATE TABLE `estadoRetiro` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `glosaEstadoRetiro` varchar(50) NOT NULL
);

CREATE TABLE `retiro` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `venta` int,
  `estadoRetiro` int,
  `sucursalRetiro` int,
  `fechaRetiro` int
);

CREATE TABLE `estadoPago` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `glosaEstadoPago` varchar(50)
);

CREATE TABLE `marca` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `nomMarca` varchar(50)
);

CREATE TABLE `imagenProducto` (
  `id` int PRIMARY KEY auto_increment,
  `producto` int,
  `imagen` varchar(100)
);

ALTER TABLE `valorProducto` ADD FOREIGN KEY (`producto`) REFERENCES `productos` (`id`);

ALTER TABLE `descuentoProducto` ADD FOREIGN KEY (`producto`) REFERENCES `productos` (`id`);

ALTER TABLE `sucursalRetiro` ADD FOREIGN KEY (`producto`) REFERENCES `productos` (`id`);

ALTER TABLE `sucursalRetiro` ADD FOREIGN KEY (`sucursal`) REFERENCES `sucursal` (`id`);

ALTER TABLE `venta` ADD FOREIGN KEY (`cliente`) REFERENCES `usuario` (`id`);

ALTER TABLE `detalleVenta` ADD FOREIGN KEY (`producto`) REFERENCES `productos` (`id`);

ALTER TABLE `detalleVenta` ADD FOREIGN KEY (`venta`) REFERENCES `venta` (`id`);

ALTER TABLE `venta` ADD FOREIGN KEY (`clienteInvitado`) REFERENCES `clienteInvitado` (`id`);

ALTER TABLE `despacho` ADD FOREIGN KEY (`venta`) REFERENCES `venta` (`id`);

ALTER TABLE `inventario` ADD FOREIGN KEY (`sucursal`) REFERENCES `sucursal` (`id`);

ALTER TABLE `pago` ADD FOREIGN KEY (`venta`) REFERENCES `venta` (`id`);

ALTER TABLE `venta` ADD FOREIGN KEY (`estadoVenta`) REFERENCES `estadoVenta` (`id`);

ALTER TABLE `sucursal` ADD FOREIGN KEY (`tipoSucursal`) REFERENCES `tipoSucursal` (`id`);

ALTER TABLE `usuario` ADD FOREIGN KEY (`rolUsuario`) REFERENCES `rolUsuario` (`id`);

ALTER TABLE `despacho` ADD FOREIGN KEY (`estadoDespacho`) REFERENCES `estadoDespacho` (`id`);

ALTER TABLE `comuna` ADD FOREIGN KEY (`provincia`) REFERENCES `provincia` (`id`);

ALTER TABLE `provincia` ADD FOREIGN KEY (`region`) REFERENCES `region` (`id`);

ALTER TABLE `sucursal` ADD FOREIGN KEY (`comunaSucursal`) REFERENCES `comuna` (`id`);

ALTER TABLE `despacho` ADD FOREIGN KEY (`comunaDespacho`) REFERENCES `comuna` (`id`);

ALTER TABLE `productoFavorito` ADD FOREIGN KEY (`usuario`) REFERENCES `usuario` (`id`);

ALTER TABLE `productoFavorito` ADD FOREIGN KEY (`producto`) REFERENCES `productos` (`id`);

ALTER TABLE `especificacionProducto` ADD FOREIGN KEY (`producto`) REFERENCES `productos` (`id`);

ALTER TABLE `opcionProducto` ADD FOREIGN KEY (`producto`) REFERENCES `productos` (`id`);

ALTER TABLE `inventario` ADD FOREIGN KEY (`producto`) REFERENCES `opcionProducto` (`id`);

ALTER TABLE `productos` ADD FOREIGN KEY (`subCatProducto`) REFERENCES `subCategoria` (`id`);

ALTER TABLE `subCategoria` ADD FOREIGN KEY (`categoria`) REFERENCES `categoria` (`id`);

ALTER TABLE `retiro` ADD FOREIGN KEY (`venta`) REFERENCES `venta` (`id`);

ALTER TABLE `retiro` ADD FOREIGN KEY (`sucursalRetiro`) REFERENCES `sucursal` (`id`);

ALTER TABLE `retiro` ADD FOREIGN KEY (`estadoRetiro`) REFERENCES `estadoRetiro` (`id`);

ALTER TABLE `pago` ADD FOREIGN KEY (`estadoPago`) REFERENCES `estadoPago` (`id`);

ALTER TABLE `productos` ADD FOREIGN KEY (`marcaProducto`) REFERENCES `marca` (`id`);

ALTER TABLE `imagenProducto` ADD FOREIGN KEY (`producto`) REFERENCES `productos` (`id`);