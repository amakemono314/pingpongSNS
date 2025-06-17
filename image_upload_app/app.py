import json
from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename

# アップロード先のフォルダと許可する拡張子
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Flaskアプリを作成
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 拡張子のチェック
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# アップロードフォームと処理
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        comment = request.form.get('comment', '')  # ← ここでフォームからコメント取得
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # コメントをJSONで保存
            metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump({'comment': comment}, f)

            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('index.html')

# アップロード完了後の表示
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return f'''
    <h1>アップロード完了！</h1>
    <img src="/static/uploads/{filename}" width="300"><br>
    <a href="/gallery">→ 投稿一覧を見る</a>
    '''

# ✅ 投稿画像の一覧表示ページ
@app.route('/gallery')
def gallery():
    image_folder = os.path.join(app.static_folder, 'uploads')
    image_files = [f for f in os.listdir(image_folder) if allowed_file(f)]

    # コメントを読み込む
    metadata = {}
    for f in os.listdir(image_folder):
        if f.endswith('.json'):
            with open(os.path.join(image_folder, f), encoding='utf-8') as mf:
                metadata[f] = json.load(mf)

    return render_template('gallery.html', images=image_files, metadata=metadata)

# アプリ起動
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
