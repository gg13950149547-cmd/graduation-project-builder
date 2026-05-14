# Integration Gate Report

## Environment
- officecli: C:\Users\Administrator\AppData\Local\OfficeCli\officecli.EXE
- renderer: Word.Application COM
- libreoffice: C:\Program Files\LibreOffice\program\soffice.exe
- wps: D:\WPS Office\12.1.0.25865\office6\wps.exe
- temp-root: C:\Users\Administrator\AppData\Local\Temp\gpb_integration_gate_0gx821d_

## Cases
- `frontmatter_roundtrip`: pass
  details: renderer=Word.Application COM; pdf=C:\Users\Administrator\AppData\Local\Temp\gpb_integration_gate_0gx821d_\frontmatter_roundtrip\stage-frontmatter\rendered.pdf; pages=6
- `lock_competition`: pass
  details: exclusive lock blocked copy, and copy succeeded after lock release
- `tail_pages_roundtrip`: pass
  details: references_page=6; acknowledgement_page=7
