"""DeepGuard - end-to-end image upload and analysis test script."""
import io
from PIL import Image as PILImage
from app import create_app
from database.db import get_db
from bson import ObjectId

app = create_app()
app.config['TESTING'] = True
db = get_db()

# Create a synthetic PNG image in memory
img = PILImage.new('RGB', (224, 224), color=(100, 150, 200))
buf = io.BytesIO()
img.save(buf, format='PNG')

db.users.delete_one({'email': 'uploadtest@deepguard.test'})

with app.test_client() as c:
    c.post('/register', data={
        'name': 'Upload Tester',
        'email': 'uploadtest@deepguard.test',
        'password': 'TestPass123!',
        'confirm_password': 'TestPass123!',
    })
    c.post('/login', data={
        'email': 'uploadtest@deepguard.test',
        'password': 'TestPass123!',
    })

    buf.seek(0)
    r = c.post(
        '/image-detection/analyze',
        data={'file': (buf, 'test_synthetic.png')},
        content_type='multipart/form-data',
        follow_redirects=False,
    )
    print('Upload response:', r.status_code, r.headers.get('Location', ''))

    if r.status_code == 302:
        location = r.headers.get('Location', '')
        r2 = c.get(location, follow_redirects=True)
        print('Result page:', r2.status_code)
        print('Has detection section:', b'Detection Result' in r2.data or b'Model Not Available' in r2.data)
        print('Has SHA-256 hash:', b'SHA-256' in r2.data)
        print('Has generate/unavailable btn:', b'Generate PDF' in r2.data or b'Model Not Available' in r2.data)

    user = db.users.find_one({'email': 'uploadtest@deepguard.test'})
    uid = ObjectId(str(user['_id']))
    analyses = list(db.analyses.find({'user_id': uid}))
    print('Analyses in MongoDB:', len(analyses))
    if analyses:
        a = analyses[0]
        print('  file_name:', a.get('file_name'))
        print('  file_hash:', str(a.get('file_hash', ''))[:16] + '...')
        print('  status:', a.get('status'))
        print('  prediction:', a.get('prediction'))

    db.analyses.delete_many({'user_id': uid})
    db.users.delete_one({'email': 'uploadtest@deepguard.test'})
    print('Cleanup done.')
