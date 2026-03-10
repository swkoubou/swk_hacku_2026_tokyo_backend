# 環境構築

## .env
以下の書式に従ってdocker-compose.yamlと同じディレクトリに配置してください
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxx
```

## 仕様
入力文章を多段階に分けて処理します
```
レベル1 janomeを用いた処理
レベル2 gpt-4.1-nanoと簡易プロンプトを用いた処理
レベル3 gpt-5-miniと通常プロンプトを用いた処理
```
/api 中核となるginのフォルダです
/lv1 レベル1のjanome + fastapiプログラムです
/