from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from main import cursor
import pymysql
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/Admin')
def admin_page():
    return render_template('admin.html')

