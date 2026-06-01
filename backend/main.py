from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Text
import sqlalchemy
from datetime import datetime
import json

DATABASE_URL = "sqlite:///./artifacts.db"
database = Database(DATABASE_URL)
metadata = MetaData()

# ========== 建表 ==========

artifacts_table = Table("artifact", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200)),
    Column("titleZh", String(200)),
    Column("period", String(200)),
    Column("dynastyId", Integer),
    Column("dynastyName", String(50)),
    Column("typeId", Integer),
    Column("typeName", String(50)),
    Column("materialId", Integer),
    Column("materialName", String(50)),
    Column("artistId", Integer),
    Column("artistName", String(100)),
    Column("descriptionZh", Text),
    Column("museumId", Integer),
    Column("museumName", String(200)),
    Column("location", String(200)),
    Column("imageUrl", String(500)),
    Column("detailUrl", String(500)),
    Column("dimensions", String(200)),
    Column("accessionNumber", String(100)),
    Column("crawlDate", String(20)),
)

museums_table = Table("museum", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200)),
    Column("nameZh", String(200)),
    Column("country", String(100)),
    Column("city", String(100)),
    Column("website", String(200)),
    Column("description", Text),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("artifactCount", Integer),
)

dynasties_table = Table("dynasty", metadata,
    Column("id", Integer, primary_key=True),
    Column("nameZh", String(50)),
    Column("nameEn", String(100)),
    Column("startYear", Integer),
    Column("endYear", Integer),
)

types_table = Table("artifact_type", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("nameEn", String(100)),
)

materials_table = Table("material", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("nameEn", String(100)),
)

artists_table = Table("artist", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100)),
    Column("nameZh", String(100)),
    Column("description", Text),
)

comments_table = Table("comment", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("artifactId", Integer),
    Column("userId", Integer),
    Column("nickname", String(100)),
    Column("content", Text),
    Column("auditStatus", String(20)),
    Column("auditRemark", String(200)),
    Column("createdAt", String(30)),
)

users_table = Table("user", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(100)),
    Column("password", String(100)),
    Column("nickname", String(100)),
    Column("phone", String(20)),
    Column("email", String(100)),
    Column("avatar", String(500)),
    Column("token", String(200)),
)

qa_table = Table("qa_message", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("userId", Integer),
    Column("question", Text),
    Column("answer", Text),
    Column("questionType", String(50)),
    Column("relatedArtifactId", Integer),
    Column("createdAt", String(30)),
)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

# ========== 初始数据 ==========

def init_data():
    with engine.connect() as conn:
        if conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM dynasty")).scalar() > 0:
            return
        conn.execute(dynasties_table.insert(), [
            {"id":1,"nameZh":"商代","nameEn":"Shang Dynasty","startYear":-1600,"endYear":-1046},
            {"id":2,"nameZh":"周代","nameEn":"Zhou Dynasty","startYear":-1046,"endYear":-256},
            {"id":3,"nameZh":"汉代","nameEn":"Han Dynasty","startYear":-206,"endYear":220},
            {"id":4,"nameZh":"唐代","nameEn":"Tang Dynasty","startYear":618,"endYear":907},
            {"id":5,"nameZh":"宋代","nameEn":"Song Dynasty","startYear":960,"endYear":1279},
            {"id":6,"nameZh":"元代","nameEn":"Yuan Dynasty","startYear":1271,"endYear":1368},
            {"id":7,"nameZh":"明代","nameEn":"Ming Dynasty","startYear":1368,"endYear":1644},
            {"id":8,"nameZh":"清代","nameEn":"Qing Dynasty","startYear":1644,"endYear":1912},
        ])
        conn.execute(types_table.insert(), [
            {"id":1,"name":"瓷器","nameEn":"Ceramics"},
            {"id":2,"name":"青铜器","nameEn":"Bronzeware"},
            {"id":3,"name":"书画","nameEn":"Painting & Calligraphy"},
            {"id":4,"name":"玉器","nameEn":"Jade"},
            {"id":5,"name":"织物","nameEn":"Textile"},
            {"id":6,"name":"雕塑","nameEn":"Sculpture"},
        ])
        conn.execute(materials_table.insert(), [
            {"id":1,"name":"陶瓷","nameEn":"Ceramic"},
            {"id":2,"name":"青铜","nameEn":"Bronze"},
            {"id":3,"name":"玉","nameEn":"Jade"},
            {"id":4,"name":"绢本","nameEn":"Silk"},
            {"id":5,"name":"纸本","nameEn":"Paper"},
            {"id":6,"name":"金","nameEn":"Gold"},
        ])
        conn.execute(artists_table.insert(), [
            {"id":1,"name":"Unknown","nameZh":"佚名","description":"作者不详"},
            {"id":2,"name":"Wang Xizhi","nameZh":"王羲之","description":"东晋著名书法家，被后人尊为书圣。"},
            {"id":3,"name":"Zhang Zeduan","nameZh":"张择端","description":"北宋画家，代表作清明上河图。"},
            {"id":4,"name":"Tang Yin","nameZh":"唐寅","description":"明代著名画家、书法家，号六如居士。"},
        ])
        conn.execute(museums_table.insert(), [
            {"id":1,"name":"The British Museum","nameZh":"大英博物馆","country":"英国","city":"伦敦","website":"https://www.britishmuseum.org","description":"大英博物馆收藏中国文物逾两万件。","latitude":51.5194,"longitude":-0.1270,"artifactCount":23000},
            {"id":2,"name":"The Metropolitan Museum of Art","nameZh":"大都会艺术博物馆","country":"美国","city":"纽约","website":"https://www.metmuseum.org","description":"大都会艺术博物馆中国馆藏涵盖五千年历史。","latitude":40.7794,"longitude":-73.9632,"artifactCount":35000},
            {"id":3,"name":"Musée du Louvre","nameZh":"卢浮宫博物馆","country":"法国","city":"巴黎","website":"https://www.louvre.fr","description":"卢浮宫收藏有大量中国古代艺术品。","latitude":48.8606,"longitude":2.3376,"artifactCount":8000},
            {"id":4,"name":"Freer Gallery of Art","nameZh":"弗利尔艺术画廊","country":"美国","city":"华盛顿","website":"https://asia.si.edu","description":"中国青铜器收藏尤为著名。","latitude":38.8881,"longitude":-77.0261,"artifactCount":5500},
            {"id":5,"name":"Victoria and Albert Museum","nameZh":"维多利亚和阿尔伯特博物馆","country":"英国","city":"伦敦","website":"https://www.vam.ac.uk","description":"中国陶瓷与纺织品收藏极为丰富。","latitude":51.4966,"longitude":-0.1722,"artifactCount":18000},
        ])
        conn.execute(artifacts_table.insert(), [
            {"id":1,"title":"Blue and White Porcelain Vase","titleZh":"青花云龙纹梅瓶","period":"Ming dynasty, Yongle period (1403-1424)","dynastyId":7,"dynastyName":"明代","typeId":1,"typeName":"瓷器","materialId":1,"materialName":"陶瓷","artistId":1,"artistName":"佚名","descriptionZh":"此梅瓶以细腻白瓷为胎，通体绘青花云龙纹，龙纹矫健有力。","museumId":1,"museumName":"大英博物馆","location":"英国伦敦","imageUrl":"https://picsum.photos/400/300?random=1","detailUrl":"https://www.britishmuseum.org","dimensions":"高 44.5 cm","accessionNumber":"PDF.A.1963.10","crawlDate":"2026-03-15"},
            {"id":2,"title":"Ritual Bronze Vessel","titleZh":"商代饕餮纹铜鼎","period":"Shang dynasty (c. 1250-1046 BC)","dynastyId":1,"dynastyName":"商代","typeId":2,"typeName":"青铜器","materialId":2,"materialName":"青铜","artistId":1,"artistName":"佚名","descriptionZh":"此铜鼎为商代晚期礼器，腹部饕餮纹线条深峻，庄严厚重。","museumId":2,"museumName":"大都会艺术博物馆","location":"美国纽约","imageUrl":"https://picsum.photos/400/300?random=2","detailUrl":"https://www.metmuseum.org","dimensions":"高 57 cm","accessionNumber":"MET.24.72.1","crawlDate":"2026-03-20"},
            {"id":3,"title":"Landscape Painting","titleZh":"仿古山水图轴","period":"Ming dynasty, 16th century","dynastyId":7,"dynastyName":"明代","typeId":3,"typeName":"书画","materialId":4,"materialName":"绢本","artistId":4,"artistName":"唐寅","descriptionZh":"此画为唐寅晚年力作，远山近水，林木苍郁。","museumId":3,"museumName":"卢浮宫博物馆","location":"法国巴黎","imageUrl":"https://picsum.photos/400/300?random=3","detailUrl":"https://www.louvre.fr","dimensions":"纵 122.5 cm","accessionNumber":"LOUVRE.OA.7234","crawlDate":"2026-03-18"},
            {"id":4,"title":"Jade Bi Disk","titleZh":"战国玉璧","period":"Warring States period (475-221 BC)","dynastyId":2,"dynastyName":"周代","typeId":4,"typeName":"玉器","materialId":3,"materialName":"玉","artistId":1,"artistName":"佚名","descriptionZh":"此玉璧以和田青玉雕琢而成，表面饰谷纹，色泽温润如脂。","museumId":4,"museumName":"弗利尔艺术画廊","location":"美国华盛顿","imageUrl":"https://picsum.photos/400/300?random=4","detailUrl":"https://asia.si.edu","dimensions":"直径 28.4 cm","accessionNumber":"FSG.F1916.345","crawlDate":"2026-03-22"},
            {"id":5,"title":"Tang Sancai Horse","titleZh":"唐三彩马","period":"Tang dynasty (618-907)","dynastyId":4,"dynastyName":"唐代","typeId":6,"typeName":"雕塑","materialId":1,"materialName":"陶瓷","artistId":1,"artistName":"佚名","descriptionZh":"唐三彩马以低温铅釉施以黄、绿、白三色，神态威武。","museumId":1,"museumName":"大英博物馆","location":"英国伦敦","imageUrl":"https://picsum.photos/400/300?random=5","detailUrl":"https://www.britishmuseum.org","dimensions":"高 73 cm","accessionNumber":"BM.1936.10.12.233","crawlDate":"2026-03-15"},
            {"id":6,"title":"Ru Ware Brush Washer","titleZh":"汝窑天青釉洗","period":"Song dynasty (960-1127)","dynastyId":5,"dynastyName":"宋代","typeId":1,"typeName":"瓷器","materialId":1,"materialName":"陶瓷","artistId":1,"artistName":"佚名","descriptionZh":"汝窑为宋代五大名窑之首，天青色釉面莹润，满布细碎开片。","museumId":5,"museumName":"维多利亚和阿尔伯特博物馆","location":"英国伦敦","imageUrl":"https://picsum.photos/400/300?random=6","detailUrl":"https://www.vam.ac.uk","dimensions":"直径 13.5 cm","accessionNumber":"VAM.C.1936.67","crawlDate":"2026-03-25"},
            {"id":7,"title":"Qingming Festival Scroll","titleZh":"清明上河图（摹本）","period":"Song dynasty (960-1279)","dynastyId":5,"dynastyName":"宋代","typeId":3,"typeName":"书画","materialId":5,"materialName":"纸本","artistId":3,"artistName":"张择端","descriptionZh":"清明上河图描绘了北宋汴京清明节前后的繁荣景象。","museumId":2,"museumName":"大都会艺术博物馆","location":"美国纽约","imageUrl":"https://picsum.photos/400/300?random=7","detailUrl":"https://www.metmuseum.org","dimensions":"纵 25.5 cm","accessionNumber":"MET.1981.276","crawlDate":"2026-03-20"},
            {"id":8,"title":"Famille Rose Bowl","titleZh":"清粉彩花卉纹碗","period":"Qing dynasty, Yongzheng (1723-1735)","dynastyId":8,"dynastyName":"清代","typeId":1,"typeName":"瓷器","materialId":1,"materialName":"陶瓷","artistId":1,"artistName":"佚名","descriptionZh":"雍正粉彩色调柔和，此碗内外满绘折枝花卉。","museumId":1,"museumName":"大英博物馆","location":"英国伦敦","imageUrl":"https://picsum.photos/400/300?random=8","detailUrl":"https://www.britishmuseum.org","dimensions":"口径 20.2 cm","accessionNumber":"BM.PDF.Y.1978.12","crawlDate":"2026-03-15"},
            {"id":9,"title":"Han Bronze Mirror","titleZh":"汉代鎏金铜镜","period":"Han dynasty (206 BC-AD 220)","dynastyId":3,"dynastyName":"汉代","typeId":2,"typeName":"青铜器","materialId":2,"materialName":"青铜","artistId":1,"artistName":"佚名","descriptionZh":"此铜镜背面鎏金，饰以四神纹，象征四方守护。","museumId":4,"museumName":"弗利尔艺术画廊","location":"美国华盛顿","imageUrl":"https://picsum.photos/400/300?random=9","detailUrl":"https://asia.si.edu","dimensions":"直径 23.4 cm","accessionNumber":"FSG.F1909.199","crawlDate":"2026-03-22"},
            {"id":10,"title":"Silk Embroidery Panel","titleZh":"清代龙袍刺绣面料","period":"Qing dynasty (1644-1912)","dynastyId":8,"dynastyName":"清代","typeId":5,"typeName":"织物","materialId":4,"materialName":"绢本","artistId":1,"artistName":"佚名","descriptionZh":"此刺绣面料为清代皇室龙袍局部，以金线绣就九龙腾云图案。","museumId":5,"museumName":"维多利亚和阿尔伯特博物馆","location":"英国伦敦","imageUrl":"https://picsum.photos/400/300?random=10","detailUrl":"https://www.vam.ac.uk","dimensions":"纵 142 cm","accessionNumber":"VAM.T.1896.23","crawlDate":"2026-03-25"},
            {"id":11,"title":"Guan Ware Vase","titleZh":"官窑粉青釉弦纹瓶","period":"Song dynasty, Southern Song (1127-1279)","dynastyId":5,"dynastyName":"宋代","typeId":1,"typeName":"瓷器","materialId":1,"materialName":"陶瓷","artistId":1,"artistName":"佚名","descriptionZh":"南宋官窑以厚釉著称，粉青釉面布满大小开片。","museumId":3,"museumName":"卢浮宫博物馆","location":"法国巴黎","imageUrl":"https://picsum.photos/400/300?random=11","detailUrl":"https://www.louvre.fr","dimensions":"高 33.6 cm","accessionNumber":"LOUVRE.G.1955.11","crawlDate":"2026-03-18"},
            {"id":12,"title":"Jade Burial Suit","titleZh":"西汉金缕玉衣（局部）","period":"Han dynasty, Western Han (206 BC-AD 9)","dynastyId":3,"dynastyName":"汉代","typeId":4,"typeName":"玉器","materialId":3,"materialName":"玉","artistId":1,"artistName":"佚名","descriptionZh":"金缕玉衣是汉代皇室贵族的葬服，以金丝连缀玉片而成。","museumId":2,"museumName":"大都会艺术博物馆","location":"美国纽约","imageUrl":"https://picsum.photos/400/300?random=12","detailUrl":"https://www.metmuseum.org","dimensions":"纵 47 cm","accessionNumber":"MET.2009.322","crawlDate":"2026-03-20"},
            {"id":13,"title":"Longquan Celadon Ewer","titleZh":"龙泉窑青瓷凤耳瓶","period":"Yuan dynasty (1271-1368)","dynastyId":6,"dynastyName":"元代","typeId":1,"typeName":"瓷器","materialId":1,"materialName":"陶瓷","artistId":1,"artistName":"佚名","descriptionZh":"龙泉窑青瓷以梅子青釉著称，釉色深沉如翡翠。","museumId":5,"museumName":"维多利亚和阿尔伯特博物馆","location":"英国伦敦","imageUrl":"https://picsum.photos/400/300?random=13","detailUrl":"https://www.vam.ac.uk","dimensions":"高 38.2 cm","accessionNumber":"VAM.C.1927.44","crawlDate":"2026-03-25"},
            {"id":14,"title":"Oracle Bone Fragment","titleZh":"商代甲骨文残片","period":"Shang dynasty (c. 1300-1046 BC)","dynastyId":1,"dynastyName":"商代","typeId":2,"typeName":"青铜器","materialId":2,"materialName":"青铜","artistId":1,"artistName":"佚名","descriptionZh":"甲骨文是中国已知最早的成熟文字，用于占卜祭祀。","museumId":1,"museumName":"大英博物馆","location":"英国伦敦","imageUrl":"https://picsum.photos/400/300?random=14","detailUrl":"https://www.britishmuseum.org","dimensions":"纵 15 cm","accessionNumber":"BM.OA.1903.4.8.3","crawlDate":"2026-03-15"},
            {"id":15,"title":"Doucai Chicken Cup","titleZh":"成化斗彩鸡缸杯","period":"Ming dynasty, Chenghua (1465-1487)","dynastyId":7,"dynastyName":"明代","typeId":1,"typeName":"瓷器","materialId":1,"materialName":"陶瓷","artistId":1,"artistName":"佚名","descriptionZh":"成化斗彩鸡缸杯是中国最名贵的瓷器之一。","museumId":2,"museumName":"大都会艺术博物馆","location":"美国纽约","imageUrl":"https://picsum.photos/400/300?random=15","detailUrl":"https://www.metmuseum.org","dimensions":"口径 8.3 cm","accessionNumber":"MET.1993.87.1","crawlDate":"2026-03-20"},
        ])
        conn.execute(comments_table.insert(), [
            {"artifactId":1,"userId":1,"nickname":"文物爱好者","content":"这件青花梅瓶造型优美，是明永乐官窑的代表作！","auditStatus":"approved","auditRemark":"","createdAt":"2026-04-10 14:23:00"},
            {"artifactId":1,"userId":2,"nickname":"历史研究生","content":"永乐年间的青花钴料来自波斯，这也是为何发色如此浓艳的原因。","auditStatus":"approved","auditRemark":"","createdAt":"2026-04-12 09:15:00"},
            {"artifactId":5,"userId":1,"nickname":"文物爱好者","content":"唐三彩马是我最喜欢的唐代文物之一！","auditStatus":"approved","auditRemark":"","createdAt":"2026-04-15 11:00:00"},
        ])
        conn.commit()

init_data()

# ========== FastAPI ==========

app = FastAPI(title="海外文物知识服务平台 API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

def ok(data):
    return {"code": 200, "message": "success", "data": data}

def paginate(lst, page, page_size):
    total = len(lst)
    start = (page - 1) * page_size
    return {"records": lst[start:start+page_size], "total": total, "page": page, "pageSize": page_size}

# ========== 1. 文物接口 ==========

@app.get("/api/artifacts/search")
async def search_artifacts(
    keyword: str,
    page: int = 1,
    pageSize: int = 20
):
    rows = await database.fetch_all(
        """
        SELECT * FROM artifact
        WHERE titleZh LIKE :kw
        OR title LIKE :kw
        OR descriptionZh LIKE :kw
        OR dynastyName LIKE :kw
        OR typeName LIKE :kw
        OR museumName LIKE :kw
        """,
        {"kw": f"%{keyword}%"}
    )

    records = []
    for row in rows:
        item = dict(row)
        records.append({
            "id": item["id"],
            "titleZh": item["titleZh"],
            "dynastyName": item["dynastyName"],
            "museumName": item["museumName"],
            "imageUrl": item["imageUrl"]
        })

    return ok(paginate(records, page, pageSize))

@app.get("/api/artifacts")
async def get_artifacts(
    page: int = 1,
    pageSize: int = 20,
    keyword: str = None,
    dynastyId: int = None,
    typeId: int = None,
    museumId: int = None
):
    q = "SELECT * FROM artifact WHERE 1=1"
    params = {}

    if keyword:
        q += """
        AND (
            titleZh LIKE :kw
            OR title LIKE :kw
            OR descriptionZh LIKE :kw
            OR dynastyName LIKE :kw
            OR typeName LIKE :kw
            OR museumName LIKE :kw
        )
        """
        params["kw"] = f"%{keyword}%"

    if dynastyId:
        q += " AND dynastyId = :dynastyId"
        params["dynastyId"] = dynastyId

    if typeId:
        q += " AND typeId = :typeId"
        params["typeId"] = typeId

    if museumId:
        q += " AND museumId = :museumId"
        params["museumId"] = museumId

    rows = await database.fetch_all(query=q, values=params)

    records = []
    for row in rows:
        item = dict(row)
        records.append({
            "id": item["id"],
            "title": item["title"],
            "titleZh": item["titleZh"],
            "dynastyName": item["dynastyName"],
            "typeName": item["typeName"],
            "museumName": item["museumName"],
            "imageUrl": item["imageUrl"]
        })

    return ok(paginate(records, page, pageSize))
@app.get("/api/artifacts/export")
async def export_artifacts(
    keyword: str = None,
    dynastyId: int = None,
    typeId: int = None,
    museumId: int = None
):
    q = "SELECT * FROM artifact WHERE 1=1"
    params = {}

    if keyword:
        q += """
        AND (
            titleZh LIKE :kw
            OR title LIKE :kw
            OR descriptionZh LIKE :kw
            OR dynastyName LIKE :kw
            OR typeName LIKE :kw
            OR museumName LIKE :kw
        )
        """
        params["kw"] = f"%{keyword}%"

    if dynastyId:
        q += " AND dynastyId = :dynastyId"
        params["dynastyId"] = dynastyId

    if typeId:
        q += " AND typeId = :typeId"
        params["typeId"] = typeId

    if museumId:
        q += " AND museumId = :museumId"
        params["museumId"] = museumId

    rows = await database.fetch_all(query=q, values=params)

    records = []
    for row in rows:
        item = dict(row)
        records.append({
            "id": item["id"],
            "titleZh": item["titleZh"],
            "title": item["title"],
            "dynastyName": item["dynastyName"],
            "typeName": item["typeName"],
            "materialName": item["materialName"],
            "period": item["period"],
            "artistName": item["artistName"],
            "museumName": item["museumName"],
            "location": item["location"],
            "dimensions": item["dimensions"],
            "accessionNumber": item["accessionNumber"],
            "detailUrl": item["detailUrl"]
        })

    return ok(records)
@app.get("/api/artifacts/export")
async def export_artifacts(
    keyword: str = None,
    dynastyId: int = None,
    typeId: int = None,
    museumId: int = None
):
    q = "SELECT * FROM artifact WHERE 1=1"
    params = {}

    if keyword:
        q += """
        AND (
            titleZh LIKE :kw
            OR title LIKE :kw
            OR descriptionZh LIKE :kw
            OR dynastyName LIKE :kw
            OR typeName LIKE :kw
            OR museumName LIKE :kw
        )
        """
        params["kw"] = f"%{keyword}%"

    if dynastyId:
        q += " AND dynastyId = :dynastyId"
        params["dynastyId"] = dynastyId

    if typeId:
        q += " AND typeId = :typeId"
        params["typeId"] = typeId

    if museumId:
        q += " AND museumId = :museumId"
        params["museumId"] = museumId

    rows = await database.fetch_all(query=q, values=params)

    records = []
    for row in rows:
        item = dict(row)
        records.append({
            "id": item["id"],
            "titleZh": item["titleZh"],
            "title": item["title"],
            "dynastyName": item["dynastyName"],
            "typeName": item["typeName"],
            "materialName": item["materialName"],
            "period": item["period"],
            "artistName": item["artistName"],
            "museumName": item["museumName"],
            "location": item["location"],
            "dimensions": item["dimensions"],
            "accessionNumber": item["accessionNumber"],
            "detailUrl": item["detailUrl"]
        })

    return ok(records)


@app.get("/api/artifacts/{id}")
async def get_artifact(id: int):
    row = await database.fetch_one(
        "SELECT * FROM artifact WHERE id = :id",
        {"id": id}
    )

    if not row:
        return {
            "code": 404,
            "message": "文物不存在",
            "data": None
        }

    item = dict(row)

    return ok({
        "id": item["id"],
        "title": item["title"],
        "titleZh": item["titleZh"],
        "period": item["period"],
        "dynastyName": item["dynastyName"],
        "typeName": item["typeName"],
        "materialName": item["materialName"],
        "artistName": item["artistName"],
        "descriptionZh": item["descriptionZh"],
        "museumName": item["museumName"],
        "location": item["location"],
        "imageUrl": item["imageUrl"],
        "detailUrl": item["detailUrl"],
        "dimensions": item["dimensions"],
        "accessionNumber": item["accessionNumber"]
    })

@app.get("/api/artifacts/{id}/recommendations")
async def get_artifact_recommendations(id: int, limit: int = 4):
    row = await database.fetch_one(
        "SELECT * FROM artifact WHERE id = :id",
        {"id": id}
    )

    if not row:
        return {
            "code": 404,
            "message": "文物不存在",
            "data": None
        }

    current = dict(row)
    rows = await database.fetch_all(
        "SELECT * FROM artifact WHERE id != :id",
        {"id": id}
    )

    rules = [
        ("museumId", 4, "同一收藏博物馆"),
        ("dynastyId", 3, "同一朝代"),
        ("typeId", 3, "同一文物类型"),
        ("materialId", 2, "同一材质"),
        ("artistId", 1, "同一作者"),
        ("location", 1, "同一收藏地点")
    ]

    records = []

    for item_row in rows:
        item = dict(item_row)
        score = 0
        reasons = []

        for field, weight, reason in rules:
            current_value = current.get(field)
            item_value = item.get(field)

            if current_value and item_value and current_value == item_value:
                score += weight
                reasons.append(reason)

        if score <= 0:
            continue

        records.append({
            "id": item["id"],
            "title": item["title"],
            "titleZh": item["titleZh"],
            "dynastyName": item["dynastyName"],
            "typeName": item["typeName"],
            "materialName": item["materialName"],
            "museumName": item["museumName"],
            "location": item["location"],
            "imageUrl": item["imageUrl"],
            "recommendScore": score,
            "recommendReason": "、".join(reasons[:3])
        })

    records.sort(key=lambda item: (-item["recommendScore"], item["id"]))

    return ok(records[:max(1, min(limit, 12))])

# ========== 2. 博物馆接口 ==========

@app.get("/api/museums")
async def get_museums(page: int = 1, pageSize: int = 20, keyword: str = None, country: str = None):
    q = "SELECT * FROM museum WHERE 1=1"
    params = {}
    if keyword:
        q += " AND (nameZh LIKE :kw OR name LIKE :kw)"
        params["kw"] = f"%{keyword}%"
    if country:
        q += " AND country = :country"
        params["country"] = country
    rows = await database.fetch_all(query=q, values=params)
    lst = [dict(r) for r in rows]
    return ok(paginate(lst, page, pageSize))

@app.get("/api/museums/{id}")
async def get_museum(id: int):
    row = await database.fetch_one("SELECT * FROM museum WHERE id = :id", {"id": id})
    if not row:
        return {"code": 404, "message": "博物馆不存在", "data": None}
    return ok(dict(row))

# ========== 3. 字典接口 ==========

@app.get("/api/dynasties")
async def get_dynasties():
    rows = await database.fetch_all("SELECT * FROM dynasty ORDER BY startYear")
    return ok([dict(r) for r in rows])

@app.get("/api/types")
async def get_types():
    rows = await database.fetch_all("SELECT * FROM artifact_type")
    return ok([dict(r) for r in rows])

@app.get("/api/materials")
async def get_materials():
    rows = await database.fetch_all("SELECT * FROM material")
    return ok([dict(r) for r in rows])

@app.get("/api/artists")
async def get_artists(keyword: str = None):
    q = "SELECT * FROM artist WHERE 1=1"
    params = {}
    if keyword:
        q += " AND (nameZh LIKE :kw OR name LIKE :kw)"
        params["kw"] = f"%{keyword}%"
    rows = await database.fetch_all(query=q, values=params)
    return ok([dict(r) for r in rows])

# ========== 4. 用户与认证接口 ==========

@app.post("/api/auth/register")
async def register(body: dict):
    username = body.get("username")
    password = body.get("password")
    existing = await database.fetch_one("SELECT id FROM user WHERE username = :username", {"username": username})
    if existing:
        return {"code": 400, "message": "用户名已存在", "data": None}
    import time
    token = f"token-{username}-{int(time.time())}"
    user_id = await database.execute(
        "INSERT INTO user (username, password, nickname, phone, email, avatar, token) VALUES (:username, :password, :nickname, :phone, :email, :avatar, :token)",
        {"username": username, "password": password, "nickname": body.get("nickname", username), "phone": body.get("phone", ""), "email": body.get("email", ""), "avatar": body.get("avatar", ""), "token": token}
    )
    return {"code": 200, "message": "注册成功", "data": {"id": user_id, "username": username, "nickname": body.get("nickname", username)}}

@app.post("/api/auth/login")
async def login(body: dict):
    username = body.get("username")
    password = body.get("password")
    user = await database.fetch_one("SELECT * FROM user WHERE username = :username", {"username": username})
    if not user:
        return {"code": 401, "message": "用户名不存在", "data": None}
    if dict(user)["password"] != password:
        return {"code": 401, "message": "密码错误", "data": None}
    user_dict = dict(user)
    return {"code": 200, "message": "登录成功", "data": {"token": user_dict["token"], "userId": user_dict["id"], "username": user_dict["username"], "nickname": user_dict["nickname"], "email": user_dict["email"], "phone": user_dict["phone"], "avatar": user_dict["avatar"]}}

@app.get("/api/auth/profile")
async def get_profile(authorization: str = Header(None)):
    if not authorization:
        return {"code": 401, "message": "未登录", "data": None}
    user = await database.fetch_one("SELECT * FROM user WHERE token = :token", {"token": authorization})
    if not user:
        return {"code": 401, "message": "token无效", "data": None}
    u = dict(user)
    return ok({"id": u["id"], "username": u["username"], "nickname": u["nickname"], "phone": u["phone"], "email": u["email"], "avatar": u["avatar"]})

# ========== 5. 评论接口 ==========

@app.get("/api/comments")
async def get_comments(artifactId: int = None, userId: int = None, page: int = 1, pageSize: int = 20):
    q = "SELECT * FROM comment WHERE auditStatus = 'approved'"
    params = {}
    if artifactId:
        q += " AND artifactId = :artifactId"
        params["artifactId"] = artifactId
    if userId:
        q += " AND userId = :userId"
        params["userId"] = userId
    rows = await database.fetch_all(query=q, values=params)
    lst = [dict(r) for r in rows]
    return ok(paginate(lst, page, pageSize))

@app.post("/api/comments")
async def post_comment(body: dict):
    user_id = body.get("userId", 0)
    nickname = "访客"
    if user_id:
        user = await database.fetch_one("SELECT nickname FROM user WHERE id = :id", {"id": user_id})
        if user:
            nickname = user["nickname"]
    comment_id = await database.execute(
        "INSERT INTO comment (artifactId, userId, nickname, content, auditStatus, auditRemark, createdAt) VALUES (:artifactId, :userId, :nickname, :content, 'pending', '', :createdAt)",
        {"artifactId": body.get("artifactId"), "userId": user_id, "nickname": nickname, "content": body.get("content"), "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    )
    return {"code": 200, "message": "评论提交成功，等待审核", "data": {"id": comment_id}}

# ========== 6. 知识问答接口 ==========

@app.post("/api/qa/ask")
async def ask_question(body: dict):
    question = body.get("question", "")
    answer = "根据知识图谱数据，暂未找到相关信息，请尝试换一种方式提问。"
    question_type = "attribute"
    related_id = None
    if "梅瓶" in question or "青花" in question:
        answer = "青花云龙纹梅瓶目前收藏于英国伦敦的大英博物馆，为明代永乐年间御窑出品，馆藏编号：PDF.A.1963.10。"
        question_type = "relation"
        related_id = 1
    elif "汝窑" in question:
        answer = "汝窑为宋代五大名窑之首，传世品极为稀少，全球存世已知不足百件。维多利亚和阿尔伯特博物馆藏有一件汝窑天青釉洗。"
        related_id = 6
    elif "大英博物馆" in question:
        answer = "根据现有数据，大英博物馆共收藏中国文物约23,000件，是海外收藏中国文物最多的博物馆之一。"
        question_type = "statistic"
    elif "唐代" in question or "唐朝" in question:
        answer = "唐代（618-907年）是中国历史的鼎盛时期。本平台收录的唐代代表性文物有：唐三彩马（大英博物馆）。"
        question_type = "relation"
        related_id = 5
    elif "清明上河图" in question or "张择端" in question:
        answer = "清明上河图是北宋画家张择端所作，大都会艺术博物馆藏有一件明代摹本。"
        related_id = 7
    await database.execute(
        "INSERT INTO qa_message (userId, question, answer, questionType, relatedArtifactId, createdAt) VALUES (:userId, :question, :answer, :questionType, :relatedArtifactId, :createdAt)",
        {"userId": body.get("userId", 0), "question": question, "answer": answer, "questionType": question_type, "relatedArtifactId": related_id, "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    )
    sources = []
    if related_id:
        row = await database.fetch_one("SELECT id, titleZh FROM artifact WHERE id = :id", {"id": related_id})
        if row:
            sources = [{"type": "artifact", "id": row["id"], "name": row["titleZh"]}]
    return ok({"question": question, "answer": answer, "questionType": question_type, "relatedArtifactId": related_id, "sources": sources})

@app.get("/api/qa/history")
async def get_qa_history(userId: int, page: int = 1, pageSize: int = 20):
    rows = await database.fetch_all("SELECT * FROM qa_message WHERE userId = :userId ORDER BY id DESC", {"userId": userId})
    lst = [dict(r) for r in rows]
    return ok(paginate(lst, page, pageSize))

@app.get("/api/qa/messages/{id}")
async def get_qa_message(id: int):
    row = await database.fetch_one("SELECT * FROM qa_message WHERE id = :id", {"id": id})
    if not row:
        return {"code": 404, "message": "记录不存在", "data": None}
    return ok(dict(row))

@app.get("/api/qa/hot")
async def get_hot_questions(limit: int = 10):
    rows = await database.fetch_all("SELECT question, COUNT(*) as count FROM qa_message GROUP BY question ORDER BY count DESC LIMIT :limit", {"limit": limit})
    if not rows:
        hot = [
            {"question": "青花瓷是哪个朝代最出名？", "count": 38},
            {"question": "大英博物馆有多少件中国文物？", "count": 31},
            {"question": "汝窑现存多少件？", "count": 27},
            {"question": "唐三彩是怎么烧制的？", "count": 24},
            {"question": "清明上河图的作者是谁？", "count": 21},
            {"question": "玉璧在古代有什么用途？", "count": 18},
            {"question": "商代青铜器有哪些代表作？", "count": 15},
            {"question": "成化斗彩为什么这么贵？", "count": 12},
        ]
        return ok(hot[:limit])
    return ok([dict(r) for r in rows])

# ========== 7. 知识图谱接口 ==========

def graph_node(prefix, item_id, label, name):
    return {
        "id": f"{prefix}_{item_id}",
        "label": label,
        "name": name
    }


def artifact_graph_node(artifact):
    return graph_node(
        "artifact",
        artifact["id"],
        "Artifact",
        artifact["titleZh"]
    )


def museum_graph_node(museum):
    return graph_node(
        "museum",
        museum["id"],
        "Museum",
        museum["nameZh"]
    )


def dynasty_graph_node(dynasty):
    return graph_node(
        "dynasty",
        dynasty["id"],
        "Dynasty",
        dynasty["nameZh"]
    )


def type_graph_node(artifact_type):
    return graph_node(
        "type",
        artifact_type["id"],
        "Type",
        artifact_type["name"]
    )


def material_graph_node(material):
    return graph_node(
        "material",
        material["id"],
        "Material",
        material["name"]
    )


def add_graph_node(nodes, node_map, node):
    if node["id"] not in node_map:
        node_map[node["id"]] = True
        nodes.append(node)


def add_graph_link(links, link_map, source, target, relation):
    key = f"{source}-{target}-{relation}"

    if key not in link_map:
        link_map.add(key)
        links.append({
            "source": source,
            "target": target,
            "relation": relation
        })


async def build_artifact_full_graph(
    artifact,
    nodes,
    links,
    node_map,
    link_map
):
    """
    构建单件文物的完整图谱：
    文物 -> 博物馆
    文物 -> 朝代
    文物 -> 类型
    文物 -> 材质

    注意：
    不新增接口，不改数据库，只补充 nodes 和 links 返回内容。
    """
    artifact_node = artifact_graph_node(artifact)
    add_graph_node(nodes, node_map, artifact_node)

    artifact_node_id = artifact_node["id"]

    # 1. 文物 -> 博物馆
    if artifact.get("museumId"):
        museum = await database.fetch_one(
            "SELECT * FROM museum WHERE id = :id",
            {"id": artifact["museumId"]}
        )

        if museum:
            museum = dict(museum)
            museum_node = museum_graph_node(museum)

            add_graph_node(nodes, node_map, museum_node)
            add_graph_link(
                links,
                link_map,
                artifact_node_id,
                museum_node["id"],
                "COLLECTED_BY"
            )

    # 2. 文物 -> 朝代
    if artifact.get("dynastyId"):
        dynasty = await database.fetch_one(
            "SELECT * FROM dynasty WHERE id = :id",
            {"id": artifact["dynastyId"]}
        )

        if dynasty:
            dynasty = dict(dynasty)
            dynasty_node = dynasty_graph_node(dynasty)

            add_graph_node(nodes, node_map, dynasty_node)
            add_graph_link(
                links,
                link_map,
                artifact_node_id,
                dynasty_node["id"],
                "BELONGS_TO_DYNASTY"
            )

    # 3. 文物 -> 类型
    if artifact.get("typeId"):
        artifact_type = await database.fetch_one(
            "SELECT * FROM artifact_type WHERE id = :id",
            {"id": artifact["typeId"]}
        )

        if artifact_type:
            artifact_type = dict(artifact_type)
            type_node = type_graph_node(artifact_type)

            add_graph_node(nodes, node_map, type_node)
            add_graph_link(
                links,
                link_map,
                artifact_node_id,
                type_node["id"],
                "HAS_TYPE"
            )

    # 4. 文物 -> 材质
    if artifact.get("materialId"):
        material = await database.fetch_one(
            "SELECT * FROM material WHERE id = :id",
            {"id": artifact["materialId"]}
        )

        if material:
            material = dict(material)
            material_node = material_graph_node(material)

            add_graph_node(nodes, node_map, material_node)
            add_graph_link(
                links,
                link_map,
                artifact_node_id,
                material_node["id"],
                "HAS_MATERIAL"
            )


def expand_keyword(keyword):
    keyword = (keyword or "").strip()
    keywords = set()

    if not keyword:
        return keywords

    keywords.add(keyword)

    if keyword.endswith("朝"):
        base = keyword[:-1]
        keywords.add(base)
        keywords.add(base + "代")

    if keyword.endswith("代"):
        base = keyword[:-1]
        keywords.add(base)
        keywords.add(base + "朝")

    alias_map = {
        "商朝": ["商代", "殷商", "商"],
        "商代": ["商朝", "殷商", "商"],
        "周朝": ["周代", "西周", "东周", "周"],
        "周代": ["周朝", "西周", "东周", "周"],
        "汉朝": ["汉代", "西汉", "东汉", "汉"],
        "汉代": ["汉朝", "西汉", "东汉", "汉"],
        "唐朝": ["唐代", "唐"],
        "唐代": ["唐朝", "唐"],
        "宋朝": ["宋代", "北宋", "南宋", "宋"],
        "宋代": ["宋朝", "北宋", "南宋", "宋"],
        "元朝": ["元代", "元"],
        "元代": ["元朝", "元"],
        "明朝": ["明代", "明"],
        "明代": ["明朝", "明"],
        "清朝": ["清代", "清"],
        "清代": ["清朝", "清"],
    }

    for item in alias_map.get(keyword, []):
        keywords.add(item)

    return keywords


def row_match(row, fields, keywords):
    for field in fields:
        value = row.get(field)

        if value is None:
            continue

        value = str(value)

        for keyword in keywords:
            if keyword in value:
                return True

    return False


@app.get("/api/graph/artifact/{id}")
async def get_artifact_graph(id: int):
    artifact = await database.fetch_one(
        "SELECT * FROM artifact WHERE id = :id",
        {"id": id}
    )

    if not artifact:
        return {
            "code": 404,
            "message": "文物不存在",
            "data": None
        }

    artifact = dict(artifact)

    nodes = []
    links = []
    node_map = {}
    link_map = set()

    await build_artifact_full_graph(
        artifact,
        nodes,
        links,
        node_map,
        link_map
    )

    return ok({
        "nodes": nodes,
        "links": links
    })


@app.get("/api/graph/museum/{id}")
async def get_museum_graph(id: int):
    museum = await database.fetch_one(
        "SELECT * FROM museum WHERE id = :id",
        {"id": id}
    )

    if not museum:
        return {
            "code": 404,
            "message": "博物馆不存在",
            "data": None
        }

    museum = dict(museum)

    artifacts = await database.fetch_all(
        "SELECT * FROM artifact WHERE museumId = :museumId",
        {"museumId": id}
    )

    nodes = []
    links = []
    node_map = {}
    link_map = set()

    museum_node = museum_graph_node(museum)
    add_graph_node(nodes, node_map, museum_node)

    for row in artifacts:
        artifact = dict(row)

        await build_artifact_full_graph(
            artifact,
            nodes,
            links,
            node_map,
            link_map
        )

    return ok({
        "nodes": nodes,
        "links": links
    })


@app.get("/api/graph/search")
async def search_graph(keyword: str):
    keywords = expand_keyword(keyword)

    if not keywords:
        return ok({
            "nodes": [],
            "links": []
        })

    artifact_rows = [
        dict(r) for r in await database.fetch_all("SELECT * FROM artifact")
    ]

    museum_rows = [
        dict(r) for r in await database.fetch_all("SELECT * FROM museum")
    ]

    dynasty_rows = [
        dict(r) for r in await database.fetch_all("SELECT * FROM dynasty")
    ]

    type_rows = [
        dict(r) for r in await database.fetch_all("SELECT * FROM artifact_type")
    ]

    material_rows = [
        dict(r) for r in await database.fetch_all("SELECT * FROM material")
    ]

    matched_artifact_ids = {
        item["id"]
        for item in artifact_rows
        if row_match(
            item,
            [
                "title",
                "titleZh",
                "period",
                "dynastyName",
                "typeName",
                "materialName",
                "museumName",
                "descriptionZh"
            ],
            keywords
        )
    }

    matched_museum_ids = {
        item["id"]
        for item in museum_rows
        if row_match(
            item,
            [
                "name",
                "nameZh",
                "country",
                "city",
                "description"
            ],
            keywords
        )
    }

    matched_dynasty_ids = {
        item["id"]
        for item in dynasty_rows
        if row_match(
            item,
            [
                "nameZh",
                "nameEn"
            ],
            keywords
        )
    }

    matched_type_ids = {
        item["id"]
        for item in type_rows
        if row_match(
            item,
            [
                "name",
                "nameEn"
            ],
            keywords
        )
    }

    matched_material_ids = {
        item["id"]
        for item in material_rows
        if row_match(
            item,
            [
                "name",
                "nameEn"
            ],
            keywords
        )
    }

    result_artifacts = []

    for artifact in artifact_rows:
        if (
            artifact["id"] in matched_artifact_ids
            or artifact["museumId"] in matched_museum_ids
            or artifact["dynastyId"] in matched_dynasty_ids
            or artifact["typeId"] in matched_type_ids
            or artifact["materialId"] in matched_material_ids
        ):
            result_artifacts.append(artifact)

    nodes = []
    links = []
    node_map = {}
    link_map = set()

    for artifact in result_artifacts:
        await build_artifact_full_graph(
            artifact,
            nodes,
            links,
            node_map,
            link_map
        )

    return ok({
        "nodes": nodes,
        "links": links
    })


@app.post("/api/admin/graph/import")
async def import_graph(data: dict):
    """
    图谱导入接口。
    目前项目使用 SQLite mock 数据，暂时返回模拟导入结果。
    接口路径和返回格式符合统一接口规范。
    """
    import_type = data.get("importType", "all")
    overwrite = data.get("overwrite", False)

    artifact_count = await database.fetch_val("SELECT COUNT(*) FROM artifact")

    return {
        "code": 200,
        "message": "导入成功",
        "data": {
            "importType": import_type,
            "overwrite": overwrite,
            "nodeCount": artifact_count * 4,
            "relationCount": artifact_count * 4
        }
    }

# ========== 新增：文物地理分布图接口 ==========
@app.get("/api/museums")
async def get_museums():
    """
    获取所有海外博物馆的列表及其坐标和藏品数量
    符合统一规范：GET /api/museums
    """
    try:
        # 1. 查询博物馆基础信息（从数据库全表的 museum 表结构衍生）
        # 如果你的 SQLite 中没有单独的 museum 表，可从 artifact 表中动态聚合，但为了符合规范，推荐从 museum 表查
        # 这里采用健壮的查询，若无单独表则从 artifact 表提取基础数据
        museums_query = """
            SELECT DISTINCT 
                museumId AS id, 
                museumName AS name,
                museumName AS name_zh, -- 示例中若无中文名，暂用原名替代
                location
            FROM artifact 
            WHERE museumId IS NOT NULL
        """
        rows = await database.fetch_all(museums_query)
        
        # 2. 统计每个博物馆的文物数量
        count_query = "SELECT museumId, COUNT(*) as c FROM artifact GROUP BY museumId"
        counts = await database.fetch_all(count_query)
        count_map = {r["museumId"]: r["c"] for r in counts}

        # 3. 模拟/匹配经纬度（因为现有的 artifact 表只有文本 location，实际项目中应当读取 museum 表的经纬度）
        # 这里给出一套预设的国际著名博物馆坐标字典，防止因数据库缺失经纬度导致地图无法渲染
        geo_mock = {
            1: {"lat": 41.5008, "lng": -81.6116, "country": "美国", "city": "克利夫兰"}, # 克利夫兰
            2: {"lat": 40.7794, "lng": -73.9632, "country": "美国", "city": "纽约"},     # 大都会
            3: {"lat": 38.8888, "lng": -77.0260, "country": "美国", "city": "华盛顿"},   # 史密斯
        }

        result = []
        for row in rows:
            m_id = row["id"]
            geo = geo_mock.get(m_id, {"lat": 40.0, "lng": -100.0, "country": "海外", "city": "未知"})
            
            result.append({
                "id": m_id,
                "name": row["name"],
                "nameZh": row["name_zh"],
                "country": geo["country"],
                "city": geo["city"],
                "latitude": geo["lat"],
                "longitude": geo["lng"],
                "artifactCount": count_map.get(m_id, 0)
            })

        return {"code": 200, "message": "success", "data": result}
    except Exception as e:
        return {"code": 500, "message": f"服务器内部错误: {str(e)}", "data": []}


# ========== 新增：统计分析看板接口 ==========
@app.get("/api/stats/dashboard")
async def get_dashboard_stats():
    """
    获取宏观统计数据：类型占比、朝代分布、博物馆藏量
    符合统一规范路径
    """
    try:
        # 1. 宏观总量统计
        total_artifacts = await database.fetch_val("SELECT COUNT(*) FROM artifact")
        total_museums = await database.fetch_val("SELECT COUNT(DISTINCT museumId) FROM artifact")
        
        # 2. 文物类型占比 (Pie Chart)
        type_query = """
            SELECT typeName AS name, COUNT(*) AS value 
            FROM artifact 
            WHERE typeName IS NOT NULL AND typeName != ''
            GROUP BY typeName 
            ORDER BY value DESC
        """
        type_stats = await database.fetch_all(type_query)
        
        # 3. 朝代分布 (Bar/Line Chart)
        dynasty_query = """
            SELECT dynastyName AS name, COUNT(*) AS value 
            FROM artifact 
            WHERE dynastyName IS NOT NULL AND dynastyName != ''
            GROUP BY dynastyName 
            ORDER BY value DESC
        """
        dynasty_stats = await database.fetch_all(dynasty_query)
        
        # 4. 博物馆藏量 Top (Bar Chart)
        museum_query = """
            SELECT museumName AS name, COUNT(*) AS value 
            FROM artifact 
            WHERE museumName IS NOT NULL AND museumName != ''
            GROUP BY museumName 
            ORDER BY value DESC
        """
        museum_stats = await database.fetch_all(museum_query)

        return {
            "code": 200,
            "message": "success",
            "data": {
                "summary": {
                    "totalArtifacts": total_artifacts,
                    "totalMuseums": total_museums
                },
                "types": [dict(r) for r in type_stats],
                "dynasties": [dict(r) for r in dynasty_stats],
                "museums": [dict(r) for r in museum_stats]
            }
        }
    except Exception as e:
        return {"code": 500, "message": f"服务器内部错误: {str(e)}", "data": {}}