import pptx

prs = pptx.Presentation(r'C:\Users\tan\.gemini\antigravity\brain\dd163c3b-15e4-4b46-9362-5f8eed45c03e\.user_uploaded\media_1794925805970_d1914cc4.pptx')
print(f'Total slides in user pptx: {len(prs.slides)}')
for idx, slide in enumerate(prs.slides):
    texts = []
    shapes_info = []
    for s in slide.shapes:
        shapes_info.append(f"{s.name}")
        if s.has_text_frame and s.text_frame.text.strip():
            texts.append(s.text_frame.text.strip().replace('\n', ' ')[:45])
    print(f"Slide {idx+1}: {len(slide.shapes)} shapes | Texts ({len(texts)}): {' // '.join(texts[:3])}")
