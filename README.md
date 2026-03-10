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
レベル2 超軽量LLMと簡易プロンプトを用いた処理
レベル3 軽量LLMと通常プロンプトを用いた処理
```
/api 中核となるginのフォルダです
/lv1 レベル1のjanome + fastapiプログラムです
/