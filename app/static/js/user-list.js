layui.use(['table', 'layer'], function () {
    var table = layui.table;
    var layer = layui.layer;

    // 渲染用户表格
    table.render({
        elem: "#users-table",
        url: "/admin/users", // 数据接口
        method: "get",
        cols: [[
            {field: "id", title: "ID", width: '8%', sort: true},
            {field: "username", title: "用户名", width: '15%'},
            {field: "nickname", title: "昵称", width: '15%'},
            {field: "email", title: "邮箱", width: '20%'},
            {field: "registertime", title: "注册时间", width: '20%'},
            {
                field: "status",
                title: "状态",
                width: '10%',
                templet: function(d) {
                    return d.status ? '<span style="color: green;">启用</span>' : '<span style="color: red;">禁用</span>';
                }
            },
            {field: 'operation', title: '操作', toolbar: '#toolbar-user', width: '12%'}
        ]],
        toolbar: '#toolbar-users',
        even: true,   // 隔行换色
        page: true,   // 开启分页
        limits: [30, 50],
        limit: 30,
        parseData: function (res) {
            // 错误处理
            if (res.code !== 20000000) {
                layer.msg('查询失败: ' + (res.message || '未知错误'), {icon: 5});
                return {
                    code: 0,
                    msg: '',
                    count: 0,
                    data: []
                };
            }
            return {
                code: res.code,
                msg: res.message,
                count: res.count || 0,
                data: res.data || []
            };
        },
        response: {
            statusCode: 20000000,  // 成功状态码（与后端一致）
            msgName: "message",
            dataName: "data"
        },
        done: function(res, curr, count) {
            // 加载完成后的错误检查
            if (res.code !== 20000000) {
                layer.msg('数据加载失败，请刷新页面重试', {icon: 5});
            }
        }
    });

    // 监听行工具事件（编辑/删除）
    table.on('tool(filter-user-table)', function (obj) {
        var data = obj.data;
        if (obj.event === 'del') {
            layer.confirm('确定删除该用户？', function (index) {
                $.ajax({
                    url: '/admin/user/' + data.id,
                    method: 'DELETE',
                    dataType: 'JSON',
                    success: function (result) {
                        if (result.code === 20002002) {  // 删除成功状态码
                            obj.del();
                            layer.close(index);
                            layer.msg(result.message, {icon: 6});
                        } else {
                            layer.msg(result.message || '删除失败', {icon: 5});
                        }
                    },
                    error: function(xhr) {
                        layer.msg('删除失败: ' + (xhr.responseJSON?.message || xhr.statusText), {icon: 5});
                    }
                });
            });
        } else if (obj.event === 'edit') {
            layer.open({
                type: 2,
                title: ['编辑用户', 'font-size:1.125rem;'],
                skin: 'layui-layer-molv',
                area: ['50%', '70%'],
                content: '/admin/user/' + data.id,
                closeBtn: 1,
                shade: 0.2,
                resize: false,
                end: function() {
                    table.reload('users-table');
                }
            });
        }
    });

    // 监听工具栏事件（添加用户）
    table.on('toolbar(filter-user-table)', function(obj) {
        if (obj.event === 'add') {
            layer.open({
                type: 2,
                title: ['添加用户', 'font-size:1.125rem;'],
                skin: 'layui-layer-molv',
                area: ['50%', '70%'],
                content: '/admin/user',
                closeBtn: 1,
                shade: 0.2,
                resize: false,
                end: function() {
                    table.reload('users-table');
                }
            });
        }
    });
});