概要
PC Auto Operation Systemは、大規模言語モデル（LLM）を使用してタスクの実行を自動化するためのモジュール式システムです。
スクリーンショットのキャプチャ、スクリプトの生成、エラーハンドリング、タスク管理およびフィードバックループの機能を備えています。
システムは高い拡張性を持ち、さまざまなAPIや通知システムと統合することが可能です。

フォルダ構成
このプロジェクトは以下のような構造になっています：

arduino
コードをコピーする
```
PC_AUTO_OPERATION_SYSTEM/
├── 設定/
│ └── settings.yaml
├── ログ/
│ ├── execution.log
│ └── operation_history.log
├── ソースコード/
│ ├── エラー処理/
│ │ ├── notification.py
│ │ └── retry_mechanism.py
│ ├── 実行/
│ │ ├── error_handler.py
│ │ └── runner.py
│ ├── フィードバックループ/
│ │ ├── checker.py
│ │ └── LLM/
│ │ ├── interface.py
│ │ └── script_generator.py
│ ├── プロンプト/
│ │ ├── プロンプト群/
│ │ │ └── prompt_1.txt
│ │ └── prompt_manager.py
│ ├── スクリーンショット/
│ │ └── capture.py
│ ├── タスク/
│ │ ├── task_manager.py
│ │ ├── task_queue.py
│ │ └── task_status.py
│ └── ユーティリティ/
│ ├── file_manager.py
│ └── logger.py
└── テスト/
├── test_capture.py
├── test_error_handler.py
├── test_runner.py
└── test_script_generator.py

```
ディレクトリの説明
config: LLM APIやSMTPサーバーの設定を含む設定ファイルが格納されています。 
data: スクリプトやスクリーンショットなど、タスク関連のデータファイルを保存します。 
logs: タスク実行やデバッグのためのログファイルが含まれています。 
src: アプリケーションのメインソースコードが含まれており、以下のモジュールに分かれています： 
error_handling: エラー通知およびリトライメカニズムを管理します。 
execution: スクリプトの実行とエラーハンドリングを管理します。 
feedback_loop: タスクの完了を確認するためのフィードバックループを実装します。 
llm: LLM APIとのやり取りや、LLMの応答に基づくスクリプト生成を行います。 
screenshot: タスクの監視のためにスクリーンショットをキャプチャします。 
task_manager: 実行するタスクのキューを管理します。 
utils: ロギングやファイル管理などのユーティリティ関数が含まれています。 
tests: システムの各コンポーネントに対するユニットテストが格納されています。 

セットアップ手順 
必要条件: Python 3.8以上がインストールされていることを確認してください。 
依存関係をインストールします： 
bash 
コードをコピーする 
pip install -r requirements.txt 
config/settings.yamlファイルを更新し、APIキーやSMTPサーバーの詳細を設定してください。 

使用方法 
メインアプリケーションを実行するには、以下のコマンドを使用します： 

bash 
コードをコピーする 
python src/main.py 
このコマンドにより、タスクマネージャーが起動し、LLMを用いてタスクを処理し、エラーを処理し、ステータスを通知します。 

設定 
LLM API: config/settings.yaml 内の llm_api_endpoint を、使用するLLMサービスのエンドポイントに更新してください。 
SMTP設定: メール通知のためにSMTPサーバーの設定を行ってください。 
テスト 
テストを実行するには、以下のコマンドを使用します： 

bash 
コードをコピーする 
python -m unittest discover tests 
このコマンドにより、すべてのユニットテストが実行され、システムコンポーネントの動作確認が行われます。 

貢献方法 
貢献を歓迎します！ リポジトリをフォークし、変更を加えた後、プルリクエストを送信してください。 

プロジェクトをフォークします。 
新しいブランチを作成します： git checkout -b feature/YourFeature 
変更をコミットします： git commit -am '新機能を追加' 
ブランチにプッシュします： git push origin feature/YourFeature 
プルリクエストを作成してください。 
大きな変更を行う前に、最初にissueを開いて変更点について議論してください。 

ライセンス 
このプロジェクトはMITライセンスのもとで提供されています。詳細についてはLICENSEファイルをご確認ください。 
