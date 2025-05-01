import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

actions = []

@app.route('/')
def index():
    image_url = actions[-1][1] if actions else None
    return render_template('index.html', image_url=image_url)

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['image']
    if file:
        img = Image.open(file.stream).convert('RGB')
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        img.save(img_path)
        actions.clear()
        actions.append(('upload', img_path))
    return redirect(url_for('index'))

@app.route('/perform_action', methods=['POST'])
def perform_action():
    action = request.form['action']
    current_image_path = actions[-1][1]
    img = Image.open(current_image_path)

    if action == 'bw':
        img = img.convert('L').convert('RGB')
    elif action == 'blur':
        img = img.filter(ImageFilter.GaussianBlur(5))
    elif action == 'flip_h':
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    elif action == 'flip_v':
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    elif action == 'vintage':
        img = ImageOps.colorize(img.convert('L'), '#704214', '#C0C0C0')
    elif action == 'cool':
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.5)
    elif action == 'warm':
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.5)
    elif action == 'brighten':
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.5)
    elif action == 'contrast':
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
    elif action == 'sharpen':
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    elif action == 'rotate':
        img = img.rotate(90, expand=True)
    elif action == 'crop':
        width, height = img.size
        left = width // 4
        top = height // 4
        right = left + width // 2
        bottom = top + height // 2
        img = img.crop((left, top, right, bottom))
    elif action == 'split_rgb':
        channel = request.form.get('channel')
        r, g, b = img.split()
        black = Image.new('L', img.size)

        if channel == 'R':
            img = Image.merge('RGB', (r, black, black))
        elif channel == 'G':
            img = Image.merge('RGB', (black, g, black))
        elif channel == 'B':
            img = Image.merge('RGB', (black, black, b))

    new_filename = f'edited_{len(actions)}.png'
    new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    img.save(new_path)
    actions.append((action, new_path))
    return redirect(url_for('index'))

@app.route('/undo', methods=['POST'])
def undo_action():
    if len(actions) > 1:
        actions.pop()
    return redirect(url_for('index'))

@app.route('/download')
def download_image():
    if actions:
        return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(actions[-1][1]), as_attachment=True)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)