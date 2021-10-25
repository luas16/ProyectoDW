var tblProducts;
var vents = {
    items: {
        cli: '',
        date_joined: '',
        subtotal: 0.00,
        iva: 0.00,
        total: 0.00,
        products: []
    },
    calculate_invoice: function () {
        var subtotal = 0.00;
        var total = 0.00;
        $.each(this.items.products, function (pos, dict) {
            dict.pos = pos;
            dict.subtotal = dict.cant * parseFloat(dict.pvp);
            subtotal += dict.subtotal;
        });
        this.items.subtotal = subtotal / 1.12;
        this.items.iva = this.items.subtotal * 0.12;
        total = this.items.subtotal + this.items.iva;
        var descuento = (($('input[name="descuento"]').val()) / 100) * total;
        this.items.total = total - (descuento);

        $('input[name="subtotal"]').val(this.items.subtotal.toFixed(2));
        $('input[name="iva"]').val(this.items.iva.toFixed(2));
        $('input[name="total"]').val(this.items.total.toFixed(2));
        $('input[name="totalDesc"]').val(descuento.toFixed(2));
    },
    add: function (item) {
        this.items.products.push(item);
        this.list();
    },
    list: function () {
        this.calculate_invoice();
        tblProducts = $('#tblProducts').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            data: this.items.products,
            columns: [
                {"data": "id"},
                {"data": "name"},
                {"data": "cate.name"},
                {"data": "pvp"},
                {"data": "cant"},
                {"data": "subtotal"},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash-alt"></i></a>';
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return 'Q.' + parseFloat(data).toFixed(2);
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="cant" class="form-control form-control-sm input-sm" autocomplete="off" value="' + row.cant + '">';
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return 'Q.' + parseFloat(data).toFixed(2);
                    }
                },
            ],
            rowCallback(row, data, displayNum, displayIndex, dataIndex) {
                $(row).find('input[name="cant"]').TouchSpin({
                    min: 1,
                    max: 1000000000,
                    step: 1
                });
            },
            initComplete: function (settings, json) {

            }
        });
    },
};

//funcion para mostrar los imagenes en select2
function formatRepo(repo) {
    //si esta iniciando y esta vacio solo mostrara un texto
    if (repo.loading) {
        return repo.text;
    }
//html para formar el listado de la busqueda por medio del select2
    var option = $(
        '<div class="wrapper container ">' +
        '<div class="row">' +
        '<div class="col-lg-1">' +
        '<img src="' + repo.image + '" class="img-fluid img-thumbnail d-block mx-auto rounded">' +
        '</div>' +
        '<div class="col-lg-5 text-left shadow-sm">' +
        '<p style="margin-bottom: 0;">' +
        '<b>Nombre:</b>' + repo.name + '<br>' +
        '<b>Categoria:</b>' + repo.cate.name + '<br>' +
        '<b>Precio:</b><span class="badge badge-warning"> Q.' + repo.pvp + '</span>' +
        '</p>' +
        '</div>' +
        '</div>' +
        '</div>');

    return option;
}

$(function () {
    $('.select2').select2({
        theme: "bootstrap4",
        language: 'es',
    });

    $('#date_joined').datetimepicker({
        format: 'YYYY-MM-DD',
        date: moment().format("YYYY-MM-DD"),
        locale: 'es',
        //minDate: moment().format("YYYY-MM-DD")
    });
    //funcion para descuentos
    $("input[name='descuento']").TouchSpin({
        min: 0,
        max: 100,
        step: 1,
        decimals: 2,
        boostat: 5,
        maxboostedstep: 10,
        postfix: '%'
    }).on('change', function () {
        vents.calculate_invoice();
    });

    // buscar productos
    // $('input[name="search"]').autocomplete({
    //     source: function (request, response) {
    //         $.ajax({
    //             url: window.location.pathname,
    //             type: 'POST',
    //             data: {
    //                 'action': 'search_products',
    //                 'term': request.term
    //             },
    //             dataType: 'json',
    //         }).done(function (data) {
    //             response(data);
    //         }).fail(function (jqXHR, textStatus, errorThrown) {
    //             //alert(textStatus + ': ' + errorThrown);
    //         }).always(function (data) {
    //
    //         });
    //     },
    //     delay: 500,
    //     minLength: 1,
    //     select: function (event, ui) {
    //         event.preventDefault();
    //         ui.item.cant = 1;
    //         ui.item.subtotal = 0.00;
    //         vents.add(ui.item);
    //         $(this).val('');
    //     }
    // });

    //eliminar todos los productos de la factura
    $('.btnEliminarTodo').on('click', function () {
        if (vents.items.products.length === 0) return false;
        alerta_eliminacion('Notificación', '¿Esta seguro de eliminar todos los productos de la factura', function () {
            vents.items.products = [];
            vents.list();
        }, function () {

        });

    });

    //evento modificar cantidad
    $('#tblProducts tbody')
        //remover un producto de la factura
        .on('click', 'a[rel="remove"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            alerta_eliminacion('Notificación', '¿Esta seguro de eliminar este producto de la factura', function () {
                vents.items.products.splice(tr.wor, 1);
                vents.list();
            }, function () {

            });

        })
        //cambiar la cantidad de un producto de la factura
        .on('change keyup', 'input[name="cant"]', function () {
            var cant = parseInt($(this).val());
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.items.products[tr.row].cant = cant;
            vents.calculate_invoice();
            $('td:eq(5)', tblProducts.row(tr.row).node()).html('Q.' + vents.items.products[tr.row].subtotal.toFixed(2));
        })

    //Guardar los datos de la factura
    $('form').on('submit', function (e) {
        e.preventDefault();
        if (vents.items.products.length === 0) {
            message_error('Debe de ingresar un producto a la factura para generarla');
            return false;
        }
        vents.items.date_joined = $('input[name="date_joined"]').val();
        vents.items.cli = $('select[name="cli"]').val();
        var parameter = new FormData();
        parameter.append('action', $('input[name="action"]').val());
        parameter.append('vents', JSON.stringify(vents.items));
        $.confirm({
            theme: 'material',
            title: 'Confirmación',
            icon: 'fa fa-info',
            content: '¿Esta seguro de realizar la siguiente accion',
            columnClass: 'medium',
            typeAnimated: true,
            cancelButtonClass: 'btn-primary',
            draggable: true,
            dragWindowBorder: false,
            buttons: {
                info: {
                    text: "Si",
                    btnClass: 'btn-primary',
                    action: function () {
                        $.ajax({
                            url: window.location.pathname,
                            type: 'POST',
                            data: parameter,
                            dataType: 'json',
                            processData: false,
                            contentType: false,
                        }).done(function (data) {
                            if (!data.hasOwnProperty('error')) {

                                alerta_eliminacion('Notificacion', '¿Desea imprimir la boleta de venta?', function () {
                                    window.open('/proyectoDW/ventas/factura/pdf/'+data.id+'/', '_blank');
                                    location.href = '/proyectoDW/ventas/list/';
                                }, function () {
                                    location.href = '/proyectoDW/ventas/list/';
                                });
                                return false;
                            }
                            message_error(data.error);
                        }).fail(function (jqXHR, textStatus, errorThrown) {
                            alert(textStatus + ': ' + errorThrown);
                        }).always(function (data) {
                        });
                    }
                },
                danger: {
                    text: "No",
                    btnClass: 'btn-red',
                    action: function () {

                    }
                },
            }
        })
    });

    //limpiar el txt para busqueda
    // $('.btnLimpiar').on('click', function () {
    //     $('input[name="search"]').val('').focus();
    // });

    //muestra el listado de mi tabla en la factura
    // vents.list();

    //buscar producto por medio de select2
    $('select[name="search"]').select2({
        theme: "bootstrap4",
        language: 'es',
        allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: window.location.pathname,
            data: function (params) {
                var queryParameters = {
                    term: params.term,
                    action: 'search_products'
                }
                return queryParameters;
            },
            processResults: function (data) {
                return {
                    results: data
                };
            },
        },
        placeholder: 'Ingrese una descripción',
        minimumInputLength: 1,
        //propiedad para mostrar la imagen
        templateResult: formatRepo,
    }).on('select2:select', function (e) {
        var data = e.params.data;
        data.cant = 1;
        data.subtotal = 0.00;
        vents.add(data);
        $(this).val('').trigger('change.select2');
    });

});


//alerta de eliminacion
function alerta_eliminacion(title, content, callback, cancel) {
    $.confirm({
        theme: 'material',
        title: title,
        icon: 'fas fa-warning',
        content: content,
        columnClass: 'medium',
        typeAnimated: true,
        cancelButtonClass: 'btn-primary',
        draggable: true,
        dragWindowBorder: false,
        buttons: {
            info: {
                text: "Si",
                btnClass: 'btn-primary',
                action: function () {
                    callback();
                }
            },
            danger: {
                text: "No",
                btnClass: 'btn-red',
                action: function () {
                    cancel()
                }
            },
        }
    })
};