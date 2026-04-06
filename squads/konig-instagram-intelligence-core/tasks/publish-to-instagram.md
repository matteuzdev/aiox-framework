---
task: Publish to Instagram
responsavel: "@instagram-chief"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - carousel_images: PNG files ready for upload
  - caption_batch: approved captions with hashtags
  - publish_manifest: post order and timing
Saida: |
  - published_posts: list of successfully published posts
  - publish_log: timestamps, URLs, and status per post
  - error_report: any failures and retry status
Checklist:
  - "[ ] All images uploaded in correct carousel order"
  - "[ ] Caption matches approved text exactly"
  - "[ ] Hashtags included and formatted correctly"
  - "[ ] Post published to correct account"
  - "[ ] Publish confirmation received"
---

# *publish-to-instagram

Publica o lote de carrosseis no Instagram via automacao com imagens, legendas e hashtags prontas.
