layui.use(['table', 'layer'], function() {
    var table = layui.table;
    var layer = layui.layer;

    //渲染表格
    table.render({
        elem: '#categories-table',
        url: '/admin/categories',
        method: 'GET',
        toolbar: '#toolbar-categories',
        request: {
            pageName: 'page',
            limitName: 'limit'
        },
        response: {
            statusName: 'code',
            statusCode: 20000000,
            msgName: 'message',
            countName: 'count',
            dataName: 'data'
        },
        cols: [[
            {field: 'id', title: 'ID', width: 80, fixed: 'left', sort: true},
            {field: 'name', title: '分类名称', width: 200},
            {field: 'description', title: '分类描述', width: 300},
            {fixed: 'right', title: '操作', toolbar: '#toolbar-category', width: 150}
        ]],
        page: true,
        limit: 10,
        limits: [10, 20, 30],
        height: 'full-120'
    });

    //监听工具栏事件
    table.on('toolbar(filter-category-table)', function(obj) {
        if (obj.event === 'add') {
            // 添加分类
            window.location.href = '/admin/category/new';
        }
    });

    //监听行工具事件
    table.on('tool(filter-category-table)', function(obj) {
        var data = obj.data;
        if (obj.event === 'del') {
            layer.confirm('确定删除该分类吗？', function(index) {
                $.ajax({
                    url: '/admin/category/' + data.id,
                    type: 'DELETE',
                    success: function(res) {
                        if (res.code === 20000000) {
                            layer.msg('删除成功', {icon: 1});
                            obj.del();
                        } else {
                            layer.msg('删除失败: ' + res.message, {icon: 2});
                        }
                    },
                    error: function() {
                        layer.msg('请求失败', {icon: 2});
                    }
                });
                layer.close(index);
            });
        } else if (obj.event === 'edit') {
            // 编辑分类
            layer.open({
                type: 2,
                title: '编辑分类',
                area: ['600px', '400px'],
                content: '/admin/category/edit/' + data.id,
                maxmin: true
            });
        }
    });
});