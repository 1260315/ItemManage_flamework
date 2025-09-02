"""
seed_data.py

テーブルに初期データを入れる
"""
from subSystems.subSystems import db, Categories, Items

def seed_data(app):
    
    with app.app_context():
        #カテゴリーのマスターデータ
        master_categories =[
            "PC",
            "モニター",
            "マウス",
            "キーボード",
            "プリンター",
            "その他"
        ]
        for category in master_categories:
            if not Categories.query.filter_by(name=category).first():
                db.session.add(Categories(name=category))


        #備品情報のテストデータ
        test_item = Items(
            name="パソコン一式",
            registrant_id=1260315,
            remark="ケーブルもあるよ!",
        )
        # 選択されたカテゴリを追加
        category_ids = [1, 2, 3, 4, 5]
        for cid in category_ids:
            category = db.session.get(Categories, int(cid))
            if category:    # categoryがNULLじゃなければ
                test_item.categories.append(category)

        db.session.add(test_item)

        db.session.commit()
        print("初期データの投入完了")