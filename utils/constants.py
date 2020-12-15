from decimal import Decimal


SYSTEM_NAME = '社内基幹システム'

REG_TEL = REG_FAX = REG_PHONE = r'^0\d{8,10}$'
REG_POST_CODE = r"^\d{7}$"
REG_BANK_CODE = r'[0-9]{4}'
REG_BANK_BRANCH_NO = r'[0-9]{3}'
REG_BANK_ACCOUNT_NO = r'[0-9]{7}'
REG_BASE64_MIME_TYPE = r'data:([A-Za-z0-9_-]+)/([.A-Za-z0-9_-]+);'
REG_BASE64_FILENAME = r'name:([^;]+);'
REG_REQUEST_NO = r"^[0-9]{7}$"
REG_PARTNER_ORDER_NO = r"^ODR[0-9]{8}$"
REG_EMAIL = r"[^\s]+@[^\s]+"
REG_NUMBER_TAIL = r'([0-9]+)$'  # 一番後ろは数字
REG_SECURITY_CODE = r'[0-9]{4}'

MIME_TYPE_EXCEL = 'application/excel'
MIME_TYPE_PDF = 'application/pdf'
MIME_TYPE_ZIP = 'application/zip'
MIME_TYPE_HTML = 'text/html'
MIME_TYPE_STREAM = 'application/octet-stream'

DEFAULT_COMPANY_CODE = 'C'
DEFAULT_WORK_LOCATION = '弊社指定場所'
DEFAULT_MEMBER_CODE_LENGTH = 7
DEFAULT_MEMBER_CODE_FORMAT = '{company_code}{org_code}{auto}'
DEFAULT_SELF_EMPLOYEE_CODE_FORMAT = 'P{org_code}{auto}'
DEFAULT_PARTNER_MEMBER_CODE_FORMAT = '{company_code}{auto}'
DEFAULT_PAID_VACATION_FORWARD_MONTH = 3  # 設定した月数で前もって有休データを作成する(単位：月)
DEFAULT_PAID_VACATION_INTERVALS = [
    (6, 18, 10),
    (18, 30, 11),
    (30, 42, 12),
    (42, 54, 14),
    (54, 66, 16),
    (66, 78, 18),
    (78, 90, 20),
]
DEFAULT_TIMEOUT = 60*30  # URL発行時間が過ぎる。(DEFAULT = 30分)

WORKING_STATUS_FORWARD = 2
PROJECT_MEMBER_MONTHLY_REQUEST_FORWARD = 0  # 今月まで案件メンバー月別請求を作成する
PARTNER_MEMBER_MONTHLY_REQUEST_FORWARD = 5  # 今月から六か月まで先の協力社員月別請求を作成
ENCRYPT_DISPLAY_VALUE = '******'  # 権限なしの場合に表示する文字列
EXPENSE_EXPORT_MAX_ROWS = 68  # 経費精算書出力時最大件数、この件数超えると出力できない、改頁が対応したら、この設定はいらない。

CHOICE_ORG_TYPE = (
    ('01', "事業部"),
    ('02', "部署"),
    ('03', "課"),
)
CHOICE_RESIDENCE_TYPE = (
    ('01', "特定活動"),
    ('02', "企業内転勤"),
    ('03', "技術・人文知識・国際業務"),
    ('10', "高度専門職1号"),
    ('11', "高度専門職2号"),
    ('20', "永住者"),
    ('21', "永住者の配偶者"),
    ('22', "日本人の配偶者"),
    ('90', "日本籍"),
)
CHOICE_GENDER = (
    ('1', "男"),
    ('2', "女"),
)
CHOICE_MARRIED = (
    ('0', "未婚"),
    ('1', "既婚"),
)
CHOICE_PAYMENT_MONTH = (
    ('1', "翌月"),
    ('2', "翌々月"),
    ('3', "３月"),
    ('4', "４月"),
    ('5', "５月"),
    ('6', "６月"),
)
CHOICE_PAYMENT_DAY = (
    ('01', '1日'),
    ('02', '2日'),
    ('03', '3日'),
    ('04', '4日'),
    ('05', '5日'),
    ('06', '6日'),
    ('07', '7日'),
    ('08', '8日'),
    ('09', '9日'),
    ('10', '10日'),
    ('11', '11日'),
    ('12', '12日'),
    ('13', '13日'),
    ('14', '14日'),
    ('15', '15日'),
    ('16', '16日'),
    ('17', '17日'),
    ('18', '18日'),
    ('19', '19日'),
    ('20', '20日'),
    ('21', '21日'),
    ('22', '22日'),
    ('23', '23日'),
    ('24', '24日'),
    ('25', '25日'),
    ('26', '26日'),
    ('27', '27日'),
    ('28', '28日'),
    ('29', '29日'),
    ('30', '30日'),
    ('99', '月末'),
)
CHOICE_TAX_RATE = (
    (Decimal('0.00'), "税なし"),
    (Decimal('0.05'), "5％"),
    (Decimal('0.08'), "8％"),
    (Decimal('0.10'), "10％"),
)
CHOICE_DECIMAL_TYPE = (
    ('0', "四捨五入"),
    ('1', "切り捨て"),
    ('2', '切り上げ'),
)
CHOICE_PROJECT_STATUS = (
    ('01', "提案"),
    ('02', "予算審査"),
    ('03', "予算確定"),
    ('10', "実施中"),
    ('90', "完了"),
)
CHOICE_PROJECT_BUSINESS_TYPE = (
    ('01', "金融（銀行）"),
    ('02', "金融（保険）"),
    ('03', "金融（証券）"),
    ('04', "製造"),
    ('05', "サービス"),
    ('90', "その他"),
)
CHOICE_ATTENDANCE_TYPE = (
    ('1', "１５分ごと"),
    ('2', "３０分ごと"),
    ('3', "１時間ごと"),
    ('4', "六分ごと"),
)
CHOICE_PROJECT_MEMBER_STATUS = (
    ('01', "提案中"),
    ('10', "作業確定"),
)
CHOICE_PROJECT_ROLE = (
    ("OP", "OP：ｵﾍﾟﾚｰﾀｰ"),
    ("PG", "PG：ﾌﾟﾛｸﾞﾗﾏｰ"),
    ("SP", "SP：ｼｽﾃﾑﾌﾟﾛｸﾞﾗﾏｰ"),
    ("SE", "SE：ｼｽﾃﾑｴﾝｼﾞﾆｱ"),
    ("SL", "SL：ｻﾌﾞﾘｰﾀﾞｰ"),
    ("L", "L：ﾘｰﾀﾞｰ"),
    ("M", "M：ﾏﾈｰｼﾞｬｰ"),
)
CHOICE_CUSTOMER_CONTRACT_TYPE = (
    ('01', "業務委託"),
    ('02', "準委任"),
    ('03', "派遣"),
    ('04', "一括"),
    # ('05', "ソフト加工"),
    ('10', "出向"),
    # ('11', "出向（在籍）"),
    # ('12', "出向（完全）"),
    ('90', "その他"),
)
CHOICE_BANK_ACCOUNT_TYPE = (
    ('01', "普通預金"),
    ('02', "定期預金"),
    ('03', "総合口座"),
    ('04', "当座預金"),
    ('05', "貯蓄預金"),
    ('06', "大口定期預金"),
    ('07', "積立定期預金")
)
CHOICE_SIMPLE_MEMBER_TYPE = (
    ('01', "社員"),
    ('02', "他社技術者"),
    ('03', "個人事業主"),
)
CHOICE_CONTRACT_TYPE = (
    ('0001', "正社員"),
    ('0002', "正社員（試用期間）"),
    ('0010', "契約社員"),
    ('0011', "パート"),
    ('0012', "アルバイト"),
    ('0020', "個人事業者"),
    ('0021', "他社技術者"),
    ('0101', "業務委託"),
    ('0102', "準委任"),
    ('0103', "派遣"),
    ('0104', "一括"),
    ('0111', "出向（在籍）"),
    ('0112', "出向（完全）"),
    ('0190', "その他"),
)
CHOICE_SALESPERSON_TYPE = (
    ('0', "営業部長"),
    ('1', "その他"),
    ('5', "営業担当"),
    ('6', "取締役"),
    ('7', "代表取締役社長"),
)
CHOICE_BUSINESS_TYPE = (
    ('01', "業務の種類（プログラマー）"),
    ('02', "業務の種類（シニアプログラマー）"),
    ('03', "業務の種類（システムエンジニア）"),
    ('04', "業務の種類（シニアシステムエンジニア）"),
    ('05', "業務の種類（課長）"),
    ('06', "業務の種類（部長）"),
    ('07', "業務の種類（営業担当）"),
    ('08', "業務の種類（マネージャー）"),
    ('09', "業務の種類（新規事業推進部担当）"),
    ('10', "業務の種類（一般社員）"),
    ('11', "業務の種類（担当課長）"),
    ('12', "業務の種類（担当部長）"),
    ('13', "業務の種類（シニアコンサルタント兼中国現地担当）"),
    ('14', "業務の種類（営業アシスタント事務）"),
    ('15', "業務の種類（経営管理業務及び管理）"),
    ('17', "業務の種類（システムエンジニア業務および課内の管理）"),
    ('18', "業務の種類（システムエンジニア業務および課内の管理補佐）"),
    ('90', "その他"),
)
CHOICE_MONTH_LIST = (
    ('01', '1月'),
    ('02', '2月'),
    ('03', '3月'),
    ('04', '4月'),
    ('05', '5月'),
    ('06', '6月'),
    ('07', '7月'),
    ('08', '8月'),
    ('09', '9月'),
    ('10', '10月'),
    ('11', '11月'),
    ('12', '12月'),
)
CHOICE_POSITION = (
    ('01', "代表取締役"),
    ('02', "取締役"),
    ('10', "事業部長"),
    ('11', "副事業部長"),
    ('20', "部長"),
    ('21', "担当部長"),
    ('30', "課長"),
    ('31', "担当課長"),
)
CHOICE_PARTNER_POSITION = (
    ('01', "代表取締役社長"),
    ('02', "取締役"),
    ('05', "営業"),
    ('10', "一般社員"),
    ('99', "その他"),
)
CHOICE_CONTRACT_STATUS = (
    ('01', "登録済み"),
    ('02', "承認待ち"),
    ('03', "承認済み"),
    ('10', "自動更新"),
    ('90', "廃棄"),
)
CHOICE_MAIL_GROUP = (
    # 社員関係
    ('0100', 'ユーザー作成通知'),
    ('0101', 'パスワード再設定'),
    # BP関係
    ('0400', '注文書と注文請書の送付'),
    ('0401', '支払通知書とBP請求書の送付'),
)
CHOICE_CONTRACT_COMMENT = (
    ('0001', '雇用期間'),
    ('0002', '職位'),
    ('0003', '就業の場所'),
    ('0004', '業務の種類'),
    ('0005', '業務の種類その他'),
    ('0006', '業務のコメント'),
    ('0007', '就業時間'),
    ('0200', '給与締め切り日及び支払日'),
    ('0201', '昇給及び降給'),
    ('0202', '賞与'),
    ('0300', '休日'),
    ('0301', '有給休暇'),
    ('0302', '無給休暇'),
    ('0800', '退職に関する項目'),
    # 一括契約に関する契約条件
    ('1000', '契約件名'),
    ('1010', '納期'),
    ('1020', '作業内容'),
    ('1021', '作業量'),
    ('1030', '納入成果品'),
    # その他の条件条件
    ('9900', 'その他備考'),
)
CHOICE_CONTRACT_TIME = (
    ('0000', '下限時間'),
    ('0001', '上限時間'),
    ('0010', '計算用下限時間'),
    ('0011', '計算用上限時間'),
)
CHOICE_CONTRACT_ALLOWANCE = (
    ('0001', '基本給（税抜）'),
    ('0002', '基本給（税金）'),
    ('0003', '基本給その他'),
    ('1000', '現場手当'),
    ('1001', '役職手当'),
    ('1002', '職務手当'),
    ('1003', '精勤手当'),
    ('1004', '安全手当'),
    ('1005', '資格手当'),
    ('1006', '通勤手当'),
    ('1007', '欠勤控除'),
    ('1008', '残業手当'),
    ('1009', '地域手当'),
    ('9900', 'その他手当'),
)
CHOICE_ALLOWANCE_UNIT = (
    ('01', '円/月'),
    ('02', '円/年'),
    ('03', '円/時間'),
    ('04', '円/日'),
    ('10', '円'),
)
CHOICE_CALCULATE_TYPE = (
    ('01', '固定１６０時間'),
    ('02', '営業日数 × ８'),
    ('03', '営業日数 × ７.９'),
    ('04', '営業日数 × ７.７５'),
    ('10', '固定金額'),
    ('11', '時給'),
    ('90', "その他（任意）"),
)
CHOICE_TAX_CATEGORY = (
    ('01', '消費税'),
)
CHOICE_EXPENSES_TYPE = (
    ('01', '自社'),  # 案件請求書に出力しない、ＢＰの場合はＢＰ請求書に出力
    ('02', '客先'),  # 案件請求書に出力
    ('10', '両方'),  # 案件請求書に出力、ＢＰの場合もＢＰ請求書に出力
)
CHOICE_DEPENDANT_TYPE = (
    ('00', '扶養外'),
    ('01', '税扶養'),
    ('02', '健保扶養'),
)
CHOICE_RELATION_SHIP = (
    ('0', '配偶者'),
    ('1', '父'),
    ('2', '母'),
    ('3', '義父'),
    ('4', '義母'),
    ('5', '子'),
    ('6', '子の配偶者'),
    ('7', '祖父'),
    ('8', '祖母'),
    ('9', '義祖父'),
    ('10', '義祖母'),
    ('11', '兄弟姉妹'),
    ('12', '兄弟姉妹の配偶者'),
    ('13', '義兄弟姉妹'),
    ('14', '孫'),
    ('15', '孫の配偶者'),
    ('16', '曽祖父'),
    ('17', '曽祖母'),
    ('18', '義曽祖父'),
    ('19', '義曽祖母'),
    ('20', '伯叔父・伯叔母'),
    ('21', '伯叔父・伯叔母の配偶者'),
    ('22', '義伯叔父・伯叔母'),
    ('23', '甥・姪'),
    ('24', '甥・姪の配偶者'),
    ('25', '義甥・姪'),
    ('26', '曾孫'),
    ('27', '曾孫の配偶者'),
    ('28', '高祖父'),
    ('29', '高祖母'),
    ('30', '大伯叔父・大伯叔母'),
    ('31', '従兄弟姉妹'),
    ('32', '大甥・姪'),
    ('33', '玄孫'),
    ('34', '高祖父の父母'),
    ('35', '曾祖伯叔父・伯叔母'),
    ('36', '従伯叔父・伯叔母'),
    ('37', '曾姪孫'),
    ('38', '来孫'),
    ('39', '高祖父の祖父母'),
    ('40', '高祖伯叔父・伯叔母'),
    ('41', '族伯叔父・伯叔母'),
    ('42', '再従兄弟姉妹'),
    ('43', '玄姪孫'),
    ('44', '昆孫'),
)
CHOICE_COUNTRY = (
    ('004', 'アフガニスタン'),
    ('008', 'アルバニア'),
    ('010', '南極'),
    ('012', 'アルジェリア'),
    ('016', 'アメリカ領サモア'),
    ('020', 'アンドラ'),
    ('024', 'アンゴラ'),
    ('028', 'アンティグア・バーブーダ'),
    ('031', 'アゼルバイジャン'),
    ('032', 'アルゼンチン'),
    ('036', 'オーストラリア'),
    ('040', 'オーストリア'),
    ('044', 'バハマ'),
    ('048', 'バーレーン'),
    ('050', 'バングラデシュ'),
    ('051', 'アルメニア'),
    ('052', 'バルバドス'),
    ('056', 'ベルギー'),
    ('060', 'バミューダ'),
    ('064', 'ブータン'),
    ('068', 'ボリビア多民族国'),
    ('070', 'ボスニア・ヘルツェゴビナ'),
    ('072', 'ボツワナ'),
    ('074', 'ブーベ島'),
    ('076', 'ブラジル'),
    ('084', 'ベリーズ'),
    ('086', 'イギリス領インド洋地域'),
    ('090', 'ソロモン諸島'),
    ('092', 'イギリス領ヴァージン諸島'),
    ('096', 'ブルネイ・ダルサラーム'),
    ('100', 'ブルガリア'),
    ('104', 'ミャンマー'),
    ('108', 'ブルンジ'),
    ('112', 'ベラルーシ'),
    ('116', 'カンボジア'),
    ('120', 'カメルーン'),
    ('124', 'カナダ'),
    ('132', 'カーボベルデ'),
    ('136', 'ケイマン諸島'),
    ('140', '中央アフリカ共和国'),
    ('144', 'スリランカ'),
    ('148', 'チャド'),
    ('152', 'チリ'),
    ('156', '中華人民共和国'),
    ('158', '中国台湾省（中華民国）'),
    ('162', 'クリスマス島'),
    ('166', 'ココス（キーリング）諸島'),
    ('170', 'コロンビア'),
    ('174', 'コモロ'),
    ('175', 'マヨット'),
    ('178', 'コンゴ共和国'),
    ('180', 'コンゴ民主共和国'),
    ('184', 'クック諸島'),
    ('188', 'コスタリカ'),
    ('191', 'クロアチア'),
    ('192', 'キューバ'),
    ('196', 'キプロス'),
    ('203', 'チェコ'),
    ('204', 'ベナン'),
    ('208', 'デンマーク'),
    ('212', 'ドミニカ国'),
    ('214', 'ドミニカ共和国'),
    ('218', 'エクアドル'),
    ('222', 'エルサルバドル'),
    ('226', '赤道ギニア'),
    ('231', 'エチオピア'),
    ('232', 'エリトリア'),
    ('233', 'エストニア'),
    ('234', 'フェロー諸島'),
    ('238', 'フォークランド（マルビナス）諸島'),
    ('239', 'サウスジョージア・サウスサンドウィッチ諸島'),
    ('242', 'フィジー'),
    ('246', 'フィンランド'),
    ('248', 'オーランド諸島'),
    ('250', 'フランス'),
    ('254', 'フランス領ギアナ'),
    ('258', 'フランス領ポリネシア'),
    ('260', 'フランス領南方・南極地域'),
    ('262', 'ジブチ'),
    ('266', 'ガボン'),
    ('268', 'ジョージア'),
    ('270', 'ガンビア'),
    ('275', 'パレスチナ'),
    ('276', 'ドイツ'),
    ('288', 'ガーナ'),
    ('292', 'ジブラルタル'),
    ('296', 'キリバス'),
    ('300', 'ギリシャ'),
    ('304', 'グリーンランド'),
    ('308', 'グレナダ'),
    ('312', 'グアドループ'),
    ('316', 'グアム'),
    ('320', 'グアテマラ'),
    ('324', 'ギニア'),
    ('328', 'ガイアナ'),
    ('332', 'ハイチ'),
    ('334', 'ハード島とマクドナルド諸島'),
    ('336', 'バチカン市国'),
    ('340', 'ホンジュラス'),
    ('344', '香港'),
    ('348', 'ハンガリー'),
    ('352', 'アイスランド'),
    ('356', 'インド'),
    ('360', 'インドネシア'),
    ('364', 'イラン・イスラム共和国'),
    ('368', 'イラク'),
    ('372', 'アイルランド'),
    ('376', 'イスラエル'),
    ('380', 'イタリア'),
    ('384', 'コートジボワール'),
    ('388', 'ジャマイカ'),
    ('392', '日本'),
    ('398', 'カザフスタン'),
    ('400', 'ヨルダン'),
    ('404', 'ケニア'),
    ('408', '朝鮮民主主義人民共和国'),
    ('410', '大韓民国'),
    ('414', 'クウェート'),
    ('417', 'キルギス'),
    ('418', 'ラオス人民民主共和国'),
    ('422', 'レバノン'),
    ('426', 'レソト'),
    ('428', 'ラトビア'),
    ('430', 'リベリア'),
    ('434', 'リビア'),
    ('438', 'リヒテンシュタイン'),
    ('440', 'リトアニア'),
    ('442', 'ルクセンブルク'),
    ('446', 'マカオ'),
    ('450', 'マダガスカル'),
    ('454', 'マラウイ'),
    ('458', 'マレーシア'),
    ('462', 'モルディブ'),
    ('466', 'マリ'),
    ('470', 'マルタ'),
    ('474', 'マルティニーク'),
    ('478', 'モーリタニア'),
    ('480', 'モーリシャス'),
    ('484', 'メキシコ'),
    ('492', 'モナコ'),
    ('496', 'モンゴル'),
    ('498', 'モルドバ共和国'),
    ('499', 'モンテネグロ'),
    ('500', 'モントセラト'),
    ('504', 'モロッコ'),
    ('508', 'モザンビーク'),
    ('512', 'オマーン'),
    ('516', 'ナミビア'),
    ('520', 'ナウル'),
    ('524', 'ネパール'),
    ('528', 'オランダ'),
    ('531', 'キュラソー'),
    ('533', 'アルバ'),
    ('534', 'シント・マールテン（オランダ領）'),
    ('535', 'ボネール、シント・ユースタティウスおよびサバ'),
    ('540', 'ニューカレドニア'),
    ('548', 'バヌアツ'),
    ('554', 'ニュージーランド'),
    ('558', 'ニカラグア'),
    ('562', 'ニジェール'),
    ('566', 'ナイジェリア'),
    ('570', 'ニウエ'),
    ('574', 'ノーフォーク島'),
    ('578', 'ノルウェー'),
    ('580', '北マリアナ諸島'),
    ('581', '合衆国領有小離島'),
    ('583', 'ミクロネシア連邦'),
    ('584', 'マーシャル諸島'),
    ('585', 'パラオ'),
    ('586', 'パキスタン'),
    ('591', 'パナマ'),
    ('598', 'パプアニューギニア'),
    ('600', 'パラグアイ'),
    ('604', 'ペルー'),
    ('608', 'フィリピン'),
    ('612', 'ピトケアン'),
    ('616', 'ポーランド'),
    ('620', 'ポルトガル'),
    ('624', 'ギニアビサウ'),
    ('626', '東ティモール'),
    ('630', 'プエルトリコ'),
    ('634', 'カタール'),
    ('638', 'レユニオン'),
    ('642', 'ルーマニア'),
    ('643', 'ロシア連邦'),
    ('646', 'ルワンダ'),
    ('652', 'サン・バルテルミー'),
    ('654', 'セントヘレナ・アセンションおよびトリスタンダクーニャ'),
    ('659', 'セントクリストファー・ネイビス'),
    ('660', 'アンギラ'),
    ('662', 'セントルシア'),
    ('663', 'サン・マルタン（フランス領）'),
    ('666', 'サンピエール島・ミクロン島'),
    ('670', 'セントビンセントおよびグレナディーン諸島'),
    ('674', 'サンマリノ'),
    ('678', 'サントメ・プリンシペ'),
    ('682', 'サウジアラビア'),
    ('686', 'セネガル'),
    ('688', 'セルビア'),
    ('690', 'セーシェル'),
    ('694', 'シエラレオネ'),
    ('702', 'シンガポール'),
    ('703', 'スロバキア'),
    ('704', 'ベトナム'),
    ('705', 'スロベニア'),
    ('706', 'ソマリア'),
    ('710', '南アフリカ'),
    ('716', 'ジンバブエ'),
    ('724', 'スペイン'),
    ('728', '南スーダン'),
    ('729', 'スーダン'),
    ('732', '西サハラ'),
    ('740', 'スリナム'),
    ('744', 'スヴァールバル諸島およびヤンマイエン島'),
    ('748', 'エスワティニ'),
    ('752', 'スウェーデン'),
    ('756', 'スイス'),
    ('760', 'シリア・アラブ共和国'),
    ('762', 'タジキスタン'),
    ('764', 'タイ'),
    ('768', 'トーゴ'),
    ('772', 'トケラウ'),
    ('776', 'トンガ'),
    ('780', 'トリニダード・トバゴ'),
    ('784', 'アラブ首長国連邦'),
    ('788', 'チュニジア'),
    ('792', 'トルコ'),
    ('795', 'トルクメニスタン'),
    ('796', 'タークス・カイコス諸島'),
    ('798', 'ツバル'),
    ('800', 'ウガンダ'),
    ('804', 'ウクライナ'),
    ('807', '北マケドニア'),
    ('818', 'エジプト'),
    ('826', 'イギリス'),
    ('831', 'ガーンジー'),
    ('832', 'ジャージー'),
    ('833', 'マン島'),
    ('834', 'タンザニア'),
    ('840', 'アメリカ合衆国'),
    ('850', 'アメリカ領ヴァージン諸島'),
    ('854', 'ブルキナファソ'),
    ('858', 'ウルグアイ'),
    ('860', 'ウズベキスタン'),
    ('862', 'ベネズエラ・ボリバル共和国'),
    ('876', 'ウォリス・フツナ'),
    ('882', 'サモア'),
    ('887', 'イエメン'),
    ('894', 'ザンビア'),
)
CHOICE_HAS_INCOME = (
    ('0', 'なし'),
    ('1', 'あり'),
)
CHOICE_DEGREE = (
    ('01', '専門職学位'),
    ('02', '短期大学士'),
    ('03', '学士'),
    ('04', '修士'),
    ('05', '博士'),
)

DICT_MONTH_EN = {
    '01': 'Jan',
    '02': 'Feb',
    '03': 'Mar',
    '04': 'Apr',
    '05': 'Mai',
    '06': 'Jun',
    '07': 'Jul',
    '08': 'Aug',
    '09': 'Sep',
    '10': 'Oct',
    '11': 'Nov',
    '12': 'Dec',
}
DICT_PROJECT_STATUS_CLASS = {
    '1': 'lime',  # 提案
    '2': 'purple',  # 予算審査
    '3': 'blue',  # 予算確定
    '4': 'green',  # 実施中
    '5': 'grey',  # 完了
}
DICT_PROJECT_MEMBER_STATUS_CLASS = {
    '1': 'lime',  # 提案中
    '2': 'green',  # 作業確定
}

CONFIG_GROUP_SYSTEM = 'system'
CONFIG_GROUP_THIRD_PART_API = 'third-part-api'
CONFIG_GROUP_EMAIL = 'email'
CONFIG_GROUP_PARTNER_ORDER = 'partner-order'
CONFIG_GROUP_FIREBASE = 'firebase'
CONFIG_GROUP_COMPANY = 'company'
CONFIG_GROUP_PAID_VACATION = 'paid-vacation'

CONFIG_FILE_SIZE_LIMIT = 'file_size_limit'
CONFIG_CONVERT_TO_PDF = 'convert_to_pdf'
CONFIG_EMAIL_ADDRESS = 'admin_email_address'
CONFIG_EMAIL_SMTP_HOST = 'admin_email_smtp_host'
CONFIG_EMAIL_SMTP_PORT = 'admin_email_smtp_port'
CONFIG_EMAIL_PASSWORD = 'admin_email_password'
CONFIG_EMAIL_SENDER = 'email_sender'
CONFIG_EMAIL_SENDER_NAME = 'email_sender_name'
CONFIG_PARTNER_ORDER_BASE_AMOUNT_COMMON = 'base_amount_common'
CONFIG_PARTNER_ORDER_BASE_AMOUNT_HOURLY = 'base_amount_hourly'
CONFIG_PARTNER_ORDER_BASE_AMOUNT_FIXED = 'base_amount_fixed'
CONFIG_PARTNER_ORDER_BASE_AMOUNT_MULTI = 'base_amount_multi'
CONFIG_PARTNER_ORDER_HOURS_MEMO = 'hours_memo'
CONFIG_PARTNER_ORDER_MINUS_PER_HOUR = 'minus_per_hour'
CONFIG_PARTNER_ORDER_PLUS_PER_HOUR = 'plus_per_hour'
CONFIG_PARTNER_ORDER_DELIVERY_PROPERTIES = 'delivery_properties'
CONFIG_PARTNER_ORDER_PAYMENT_CONDITION = 'payment_condition'
CONFIG_PARTNER_ORDER_CONTRACT_ITEMS = 'contract_items'
CONFIG_FIREBASE_IID_TOKEN = 'iid_token'
CONFIG_FIREBASE_TOPIC_LIST = 'topic_list'
CONFIG_FIREBASE_TOPIC_CREATE = 'topic_create'
CONFIG_COMPANY_MEMBER_CODE_LENGTH = 'member_code_length'
CONFIG_COMPANY_MEMBER_CODE = 'member_code'
CONFIG_COMPANY_SELF_EMPLOYEE_CODE = 'self_employee_code'
CONFIG_COMPANY_PARTNER_MEMBER_CODE = 'partner_member_code'
CONFIG_PAID_VACATION_FORWARD_MONTH = 'forward_month'
CONFIG_PAID_VACATION_INTERVALS = 'interval_months'
CONFIG_SYSTEM_DOMAIN = 'domain'

ERROR_ORG_TYPE_PARENT = '組織類別と親組織は一致していません。'
ERROR_ORG_POSITION = '組織類別と合わない職位です。'
ERROR_DELETE_PROTECTED = '関連付けの {name} が存在しますので、削除できません。'
ERROR_OBJECT_DUPLICATE = '{name}が重複しています。'
ERROR_DUPLICATED_PROJECT_MEMBER = 'メンバー{name}が期間（{start}～{end}）内で重複登録しています。'
ERROR_DUPLICATED_OVER_THREE = '三つの案件以上同時にアサインしましたので、削除できません、管理員にご連絡ください。'
ERROR_DUPLICATED_ORDER_MEMBER = '注文書{order_no}({start}～{end})と重複しています。'
ERROR_COST_PERCENTAGE_OVER = '{year}年{month}月の割合合計が1を超えました。'
ERROR_DATE_CONFLICT = '日付 {date} が重複しています。'
ERROR_DATE_CONFLICT_TO = '日付 {date} が既存の「{object}」に重複しています。'
ERROR_DATE_CONTRADICT = '{start} と {end} の期間が不正です。'
ERROR_DATE_FINISHED_MONTH = "終了年月「{year}年{month}月」は不正です、開始年月以降に選択してください。"
ERROR_DATA_DISCORDANCE = '違う{name}が存在しています、同じ{name}のを使用してください。'
ERROR_NO_SALESPERSON = '{name}の営業員は設定されていません。'
ERROR_NOT_IMPLEMENTED = '未実装です。'
ERROR_NO_CONTRACT = '{name}の契約がありません。'
ERROR_NO_CONTRACT_FOR_WORKING_STATUS = '{name}は{year}年{month}月の契約がありません。'
ERROR_NO_BLANKET_CONTRACT_FOR_CREATE_REQUEST = '{name}の{year}年{month}月一括契約がないので、請求書作成できません。'
ERROR_NO_CONTRACT_PERIOD = '{name}は{start}～{end}期間内の契約がありません。'
ERROR_NO_PARTNER_CONTRACT = '{name}は{company}の契約がありません。'
ERROR_NO_CALCULATE_HOURS = '{condition}の場合、契約計算用時間が必要ないです。'
ERROR_NO_MONTHLY_REQUEST_FOR_CREATE = '{year}年{month}月の精算条件がまだ作成されてないので、{name}は作成できません。'
ERROR_NO_EMAIL = '{name}のメールアドレスが設定されていません。'
ERROR_NO_EMAIL_RECIPIENT = '宛先がありません。'
ERROR_NO_EMAIL_TEMPLATE = 'メールテンプレートが設定されていません、管理サイトにてご設定ください。'
ERROR_NO_PERMISSION = '権限がありません。'
ERROR_NO_CONTENT_IN_YM = '{name}が{year}年{month}月に{content}はありません。'
ERROR_NO_IMPLEMENTATION = '{name}は実装されていません。'
ERROR_NO_TOPIC = 'トピック:{topic}がありません、{process}はできません。'
ERROR_NO_PAID_VACATION = '有休がありません。'
ERROR_NO_EXPENSES = '{name}は{year}年{month}月に経費申請がありません。'
ERROR_NO_PROJECTS = '{name}はまだ案件にアサインしていません。'
ERROR_NO_ORGANIZATION_FOR_PROJECT = '{name}は所属部署がありません、所属案件があるかどうかをご確認ください。'
ERROR_EXPENSE_COUNT_OVER = '{name}は{year}年{month}月の経費件数制限は超過しました、{count}件以下にしてください。'
ERROR_MULTI_PARTNER_CONTRACT = '{name}は{company}の契約が複数あります。'
ERROR_MULTI_SALESPERSON = '{name}の営業員は複数います。'
ERROR_MULTI_CONTENT_IN_YM = '{name}が{year}年{month}月に{content}は複数あります。'
ERROR_UNKNOWN_ATTACHMENT = '識別できないファイルです。'
ERROR_UNKNOWN_CATEGORY = '処理できません。'
ERROR_UNKNOWN_MEMBER_TYPE = '識別できないメンバーの種類です。'
ERROR_DATA_NOT_FOUND = '{name}が見つかりません。'
ERROR_DATA_NOT_FOUND_FOR_REASON = '{name}が見つかりません、{reason}。'
ERROR_FILE_NOT_FOUND = 'ファイル {name} は見つかりません。'
ERROR_FILE_SIZE_LIMIT = 'ファイルは大きすぎます、{limit}以下のファイルをアップロードしてください。'
ERROR_REQUIRE_CALCULATE_HOURS = '{condition}の場合、契約計算用時間の設定が必要です。'
ERROR_REQUIRE_MAX_HOURS = '{condition}の場合、上限時間の設定が必要です。'
ERROR_REQUIRE_FIELD = '{name} は必須項目です。'
ERROR_REQUIRE_FIELD_CASE = '{condition}の場合、{name} は必須項目です。'
ERROR_REQUIRE_DATA = '{name} は必要です。'
ERROR_REQUIRE_NEITHER = '{name1}または{name2}は必要です。'
ERROR_REQUIRE_ATTENDANCE = '{name}は{year}年{month}月の勤務時間が未入力です。'
ERROR_REQUIRE_PROJECT = 'まだ案件にアサインしていないメンバーがいます。'
ERROR_MULTIPLE_COMPANY_YM = '{name} が同じ会社かつ同じ年月であることが必要です。'
ERROR_UNCOMPLICATED_PAYMENT_NOTICE = '支払通知書はまだ全部作成されていません。'
ERROR_ORGANIZATION_POSITION = '{org_type} の場合 {value} は選択できません。'
ERROR_DATA_SAVE_ERROR = '{name}保存失敗しました。'
ERROR_DATA_DUPLICATE = 'データは重複しています。'
ERROR_MAIL_GROUP_NOT_FOUND = 'メールグループ {name} は設定されていません。'
ERROR_MAIL_GROUP_MULTI_FOUND = 'メールグループ {name} は複数設定されています。'
ERROR_UNIQUE = '{name} は一意でなければなりません。'
ERROR_PROJECT_NO_MEMBER = '{name} にメンバーがアサインされていません。'
ERROR_PROJECT_MEMBER_NO_REQUEST = '案件 {name} にメンバー月別請求が作成されていません。'
ERROR_PROJECT_MEMBER_RELEASED = '{name} がこの注文書の期間{start}～{end}に稼働していません。'
ERROR_CANNOT_CHANGE_TOPIC_NAME = 'トピック名称は変更できません、削除してから追加してください。'
ERROR_CANNOT_CHANGE_OBJECT = '既に{reason}なので、{name}が変更できません。'
ERROR_CANNOT_DELETE_CONTRACT = '{reason}ので、契約を削除できません。'
ERROR_CANNOT_CREATE_MULTI_ORDERS = '精算条件が不一致なので、BP注文書はまとめて作成できません。'
ERROR_CANNOT_CREATE_NO_ORDERS = '注文書がないため、{name}作成できません。'
ERROR_CANNOT_CREATE_ORDER_ON_SECOND_REQUEST = 'この注文書は{start}～{end}で作成されているので、再作成するには{start}で作成してください。'
ERROR_CANNOT_CREATE_FOR_SENT = '{name} が既に送信済みなので、再作成はできません。'
ERROR_CANNOT_ESTABLISH_CONNECTION = '{name}に接続できません。'
ERROR_CANNOT_RETIRE_FOR_PROJECT = '案件{name}はまだ稼働中なので、退場できません。本当に退場したい場合は案件のアサイン終了日を変更してください。'
ERROR_CANNOT_ASSIGN_MEMBER = '案件は既に終了しましたので、アサインできません。'
ERROR_PICK_ONLY_ONE = '{name}のどっちか一つを入力してください。'
ERROR_MEMBER_NO_EMAIL = '{name}のメールアドレスが設定されていません。'
ERROR_INVALID_DATA = '{value}有効な{name}ではありません。'
ERROR_INVALID_IMAGE_EXT = "サポートしないファイルです、{ext}ファイルをアップロードしてください。"
ERROR_EMAIL_AUTHENTICATION = 'メールサーバー認証失敗しました。'
ERROR_EMAIL_ALREADY_SENT = 'メールは既に送信済みです。'
ERROR_CONFIG_EMAIL_SERVER = 'システム設定にメール送信サーバーが設定不正です。'
ERROR_CONTRACT_INVALID_AUTO_UPDATE_FLG = '契約形態{contract_type}の場合、自動更新はできません。'
ERROR_CONTRACT_REQUIRE_AUTO_UPDATE_FLG = '契約形態{contract_type}の場合、自動更新は必要となります。'
ERROR_REGISTER_TOPIC = 'トピック登録失敗({exception})。'
ERROR_REGISTER_DEVICE_TO_TOPIC = '{name}のデバイス({device})をトピック({topic})に登録失敗しました。'
ERROR_UNREGISTER_DEVICE_TO_TOPIC = '{name}のデバイス({device})をトピック({topic})から解除に失敗しました。'
ERROR_DIRTY_DATA = '{name}は既に変更済みなので、最新のデータを取得してください。'
ERROR_FILE_FORMAT = '{name}はテンプレートにあっていません、最新のファイルを使用してください。'
ERROR_CSV_FORMAT = '{name}のフォーマットはに識別できません。'
ERROR_BP_ORDER_NOT_COMPLETED = 'ＢＰ注文書は全部作成されていません。'
ERROR_CONTRACT_ITEM_BUSINESS_TYPE = '業務の種類は不正です。'
ERROR_PAID_VACATION_USAGE = '今年申請した有休日数が{days}を超えました。'
ERROR_PAID_VACATION_INVALID_DAYS = '{date}に申請した日数は有効ではありません。'
ERROR_URL_TIMEOUT = 'URLの時間が過ぎましたので、もう一度最初からやり直してください！'
ERROR_SECURITY_CODE_CONFIRM = '認証コード一致していません、もう一度入力してください。'
ERROR_SECURITY_CODE_TIMES = '認証コード入力回数が３回以上超えましたので、もう一度最初からやり直してください。'

INFO_FILE_UPLOADED = '写真アップロードしました。'
INFO_PASSWORD_SENT = '{title}のパスワードは送信しました。'
INFO_EMAIL_SENT = '題名: {title}; TO: {to}; CC: {cc}; BCC: {bcc} 送信完了。'
INFO_CREATED_COUNT = '{success}/{count}件の{name}が作成されました。'
INFO_DELETED_COUNT = '{success}/{count}件の{name}が削除されました。'
INFO_CONTRACT_AUTO_UPDATED = '{name}（{start_date}～{end_date}）が作成されました。'
INFO_CONTRACT_UPDATED_COUNT = '{count}件の契約が更新されました。'
INFO_FIREBASE_DEVICE_REGISTER = '{name}のデバイス({device})をトピック({topic})に登録しました。'
INFO_FIREBASE_DEVICE_UNREGISTER = '{name}のデバイス({device})をトピック({topic})から解除しました。'
INFO_FIREBASE_SEND_MESSAGE = 'トピック({topic})にメッセージを送信しました。'
INFO_FIREBASE_NO_DEVICE = 'トピック({topic})に登録したデバイスがありません。'

WARN_NO_CONTRACT = '{name}に{year}年{month}月に契約がありません。'

NAME_PARTNER_REQUEST = '{company}{year}年{month}月_{organization}'
NAME_ORGANIZATION_ATTENDANCE = "勤怠情報_{organization}_{year}年{month}月_{timestamp}"
NAME_WORKER_ROSTER = '労働者名簿'
NAME_WORKER_ROSTER_BY_MEMBER = '労働者名簿_{name}'
NAME_EXPENSE_BY_MEMBER = '経費精算書_{name}_{year}年{month}月'

LABEL_BP_ORDER_DEFAULT_LOCATION = "弊社指定場所"

FORMAT_ATTENDANCE_TITLE1 = (
    'No', 'Content Type ID', 'Object ID', 'Project ID',
    '基本データ', None, None, None, None,
    '案件情報', None, None, None,
    '勤務情報', None, None, None, None, None, None
)
FORMAT_ATTENDANCE_TITLE2 = (
    None, None, None, None,
    '社員番号', '氏名', '所在部署', '所属会社', '契約形態',
    '案件名', '最寄駅', '顧客会社', '契約種類',
    '勤務時間', 'ＢＰ勤務時間', '勤務日数', '深夜日数', '客先立替金', '立替金', '通勤交通費'
)
FORMAT_SALARY_CSV_TITLE = (
    '事業所番号', '事業所名', '所属Ⅰ番号', '所属Ⅰ名', '所属Ⅱ番号', '所属Ⅱ名', '役職名', '社員番号', '社員氏名', '年', '月', '賃金支払対象期間(開始)', '賃金支払対象期間(終了)',
    '支払日', '役員報酬', '基本給', '基本給2', '基本給3', '職務手当', '住宅手当', '地域手当', '給与手当04', '給与手当05', '給与手当06', '給与手当07', '給与手当08',
    '給与手当09', '給与手当10', '給与手当11', '給与手当12', '給与手当13', '給与手当14', '給与手当15', '給与手当16', '時間外手当', '給与手当18', '給与手当19',
    '給与手当20', '給与手当21', '給与手当22', '給与手当23', '法定内休出手', '法定外休出手', '給与手当26', '深夜手当', '給与手当28', '給与手当29', '通勤手当', '年特休手当',
    '代休手当', '臨時手当1', '臨時手当2', '臨時手当3', '臨時手当4', '臨時手当5', '臨時手当6', '臨時手当7', '臨時手当8', '差額追給(課税)', '差額追給(非課税)', '欠勤控除',
    '遅早控除', '減額1', '減額2', '給与総額', '労災保険対象', '雇用保険対象', '基本基礎1', '基本基礎2', '基本基礎3', '割増基礎', '非課税対象', '課税給与', '課税対象',
    '健康保険', '健康保険(内訳)基本保険料', '健康保険(内訳)特定保険料', '介護保険', '厚生年金', '厚生年金基金', '雇用保険', '社保合計', '所得税', '住民税', '給与控除01',
    '給与控除02', '給与控除03', '年末調整', '立替経費', '立替経費調整', '給与控除07', '給与控除08', '給与控除09', '給与控除10', '年調過不足', '臨時控除', '貸付金返済',
    '端数預金控除', '控除合計', '端数預金払戻', '差引支給', '現金支給', '振込支給1', '振込支給2'
)
