# يضيف صلاحية الكاميرا + يخلي التطبيق يظهر في "فتح بـ" لملفات .accdata (ملفات تيليجرام)
p = 'android/app/src/main/AndroidManifest.xml'
s = open(p, encoding='utf-8').read()

if 'android.permission.CAMERA' not in s:
    s = s.replace('<application', '<uses-permission android:name="android.permission.CAMERA" />\n    <application', 1)

# السماح ببدء مُثبّت أندرويد عند تنزيل تحديث APK من داخل التطبيق
if 'android.permission.REQUEST_INSTALL_PACKAGES' not in s:
    s = s.replace('<application', '<uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />\n    <application', 1)

flt = '''
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="content" />
                <data android:scheme="file" />
                <data android:host="*" />
                <data android:mimeType="*/*" />
                <data android:pathPattern=".*\\\\.accdata" />
                <data android:pathPattern=".*\\\\..*\\\\.accdata" />
                <data android:pathPattern=".*\\\\..*\\\\..*\\\\.accdata" />
                <data android:pathPattern=".*\\\\..*\\\\..*\\\\..*\\\\.accdata" />
            </intent-filter>
'''
if 'accdata' not in s:
    s = s.replace('</activity>', flt + '        </activity>', 1)

open(p, 'w', encoding='utf-8').write(s)
print('manifest patched')

# تفعيل تكبير/تصغير الشاشة باللمس (pinch-to-zoom) جوه التطبيق
import re, glob
main_files = glob.glob('android/app/src/main/java/**/MainActivity.java', recursive=True)
if not main_files:
    print('WARNING: MainActivity.java not found, skipping zoom patch')
for mp in main_files:
    ms = open(mp, encoding='utf-8').read()
    if 'setBuiltInZoomControls' in ms:
        continue
    if 'import android.webkit.WebSettings;' not in ms:
        ms = ms.replace('import com.getcapacitor.BridgeActivity;',
                         'import android.os.Bundle;\nimport android.webkit.WebSettings;\nimport com.getcapacitor.BridgeActivity;', 1)
    on_create = '''
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WebSettings ws = this.bridge.getWebView().getSettings();
        ws.setSupportZoom(true);
        ws.setBuiltInZoomControls(true);
        ws.setDisplayZoomControls(false);
    }
'''
    ms2 = re.sub(r'(class\s+MainActivity\s+extends\s+BridgeActivity\s*\{)', r'\1' + on_create, ms, count=1)
    if ms2 == ms:
        print('WARNING: could not patch zoom in', mp)
    else:
        open(mp, 'w', encoding='utf-8').write(ms2)
        print('zoom enabled in', mp)
