layui.use(['table', 'layer'], function () {
    var table = layui.table;
    var layer = layui.layer;

    table.render({
        elem: "#tags-table",
        url: "/admin/tags", // 需实现标签列表API
        method: "get",
        cols: [[
            {field: "id", title: "ID", width: '10%', sort: true},
            {field: "name", title: "标签名", width: '60%'},
            {field: 'operation', title: '操作', toolbar: '#toolbar-tag', width: '30%'}
        ]],
        toolbar: '#toolbar-tags',
        even: true,
        page: true,
        limits: [30, 50],
        limit: 30
    });

    // 监听工具栏事件
    table.on('toolbar(filter-tag-table)', function (obj) {
        if (obj.event === 'add') {
            location.href = '/admin/tag'; // 跳转到创建标签页面
        }
    });

    // 监听行操作事件
    table.on('tool(filter-tag-table)', function (obj) {
        var data = obj.data;
        if (obj.event === 'del') {
            layer.confirm('确定删除？', function (index) {
                $.ajax({
                    url: '/admin/tag/' + data.id,
                    method: 'DELETE',
                    success: function (res) {
                        if (res.code === 20000000) {
                            obj.del();
                            layer.close(index);
                            layer.msg('删除成功');
                        } else {
                            layer.msg('删除失败: ' + res.message);
                        }
                    }
                });
            });
        } else if (obj.event === 'edit') {
            location.href = '/admin/tag/' + data.id + '/edit';
        }
    });
});