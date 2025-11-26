"""
任务管理API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
import json

# 修复导入路径
from backend.database.db import get_db
from backend.models.task import TaskLog

bp = Blueprint('tasks', __name__)

@bp.route('/logs', methods=['GET'])
@jwt_required()
def get_task_logs():
    """获取任务日志列表"""
    # 查询参数
    site_id = request.args.get('site_id', type=int)
    task_type = request.args.get('task_type')
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 构建查询条件
        where_clauses = []
        params = []
        
        if site_id:
            where_clauses.append('site_id = ?')
            params.append(site_id)
        
        if task_type:
            where_clauses.append('task_type = ?')
            params.append(task_type)
        
        if status:
            where_clauses.append('status = ?')
            params.append(status)
        
        if start_date:
            where_clauses.append('executed_at >= ?')
            params.append(start_date)
        
        if end_date:
            where_clauses.append('executed_at <= ?')
            params.append(end_date)
        
        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'
        
        # 查询总数
        cursor.execute(f'SELECT COUNT(*) FROM task_logs WHERE {where_sql}', params)
        total = cursor.fetchone()[0]
        
        # 查询日志
        offset = (page - 1) * per_page
        params.extend([per_page, offset])
        
        cursor.execute(f'''
            SELECT tl.*, s.name as site_name
            FROM task_logs tl
            LEFT JOIN sites s ON tl.site_id = s.id
            WHERE {where_sql}
            ORDER BY executed_at DESC
            LIMIT ? OFFSET ?
        ''', params)
        
        rows = cursor.fetchall()
        logs = []
        for row in rows:
            log_dict = dict(row)
            if log_dict.get('details'):
                log_dict['details'] = json.loads(log_dict['details'])
            logs.append(log_dict)
        
        return jsonify({
            'total': total,
            'page': page,
            'per_page': per_page,
            'logs': logs
        }), 200

@bp.route('/logs/<int:log_id>', methods=['GET'])
@jwt_required()
def get_task_log(log_id):
    """获取单个任务日志详情"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT tl.*, s.name as site_name
            FROM task_logs tl
            LEFT JOIN sites s ON tl.site_id = s.id
            WHERE tl.id = ?
        ''', (log_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': '任务日志不存在'}), 404
        
        log_dict = dict(row)
        if log_dict.get('details'):
            log_dict['details'] = json.loads(log_dict['details'])
        
        return jsonify(log_dict), 200

@bp.route('/logs', methods=['DELETE'])
@jwt_required()
def clear_old_logs():
    """清理旧日志"""
    days = request.args.get('days', 30, type=int)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('DELETE FROM task_logs WHERE executed_at < ?', (cutoff_date,))
        deleted_count = cursor.rowcount
        conn.commit()
        
        return jsonify({
            'message': f'已清理 {deleted_count} 条日志',
            'deleted_count': deleted_count
        }), 200

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """获取任务统计信息"""
    days = request.args.get('days', 7, type=int)
    
    with get_db() as conn:
        cursor = conn.cursor()
        start_date = datetime.now() - timedelta(days=days)
        
        # 按状态统计
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM task_logs
            WHERE executed_at >= ?
            GROUP BY status
        ''', (start_date,))
        
        status_stats = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # 按任务类型统计
        cursor.execute('''
            SELECT task_type, COUNT(*) as count
            FROM task_logs
            WHERE executed_at >= ?
            GROUP BY task_type
        ''', (start_date,))
        
        type_stats = {row['task_type']: row['count'] for row in cursor.fetchall()}
        
        # 按站点统计
        cursor.execute('''
            SELECT s.name, COUNT(*) as count
            FROM task_logs tl
            LEFT JOIN sites s ON tl.site_id = s.id
            WHERE tl.executed_at >= ?
            GROUP BY s.name
        ''', (start_date,))
        
        site_stats = {row['name']: row['count'] for row in cursor.fetchall()}
        
        # 每日统计
        cursor.execute('''
            SELECT DATE(executed_at) as date, COUNT(*) as count, status
            FROM task_logs
            WHERE executed_at >= ?
            GROUP BY DATE(executed_at), status
            ORDER BY date DESC
        ''', (start_date,))
        
        daily_stats = {}
        for row in cursor.fetchall():
            date = row['date']
            if date not in daily_stats:
                daily_stats[date] = {}
            daily_stats[date][row['status']] = row['count']
        
        return jsonify({
            'status_stats': status_stats,
            'type_stats': type_stats,
            'site_stats': site_stats,
            'daily_stats': daily_stats,
            'period_days': days
        }), 200

@bp.route('/run/<int:site_id>', methods=['POST'])
@jwt_required()
def run_task_manually(site_id):
    """手动运行任务"""
    data = request.get_json() or {}
    task_types = data.get('task_types', ['signin', 'reply'])
    
    # TODO: 实现手动运行任务的逻辑
    # 这里应该调用调度器来执行任务
    
    return jsonify({
        'message': '任务已加入执行队列',
        'site_id': site_id,
        'task_types': task_types
    }), 202
