# EDINET-API
EDINETサイトからAPI機能を利用して開示データをダウンロードするプログラム。
前回の取得データ以降～当日のプログラム実行時点までの開示データ（有価証券報告書、半期報告書、四半期報告書）が取得可能。

ベータ版として、PDFのみ取得可能となっている。

# 使い方
pythonプログラム内のTMP_DIRをご自身の環境に合わせて修正のうえ、実行する。
一度に取得可能な開示文書数は100に設定してある。再度実施すれば、前回の取得以降の開示データが取得可能。

# 環境
pythonが使用可能であること。
またdatetime、json、os、requests、sysをimportしているため、インストールしておくこと。

# 作成者情報
Author:Shintaro Nakai
e-mail:shintaro.nakai7140@gmail.com
