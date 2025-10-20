# Suspect Face Matching Feature - User Guide

## Overview

The **Suspect Face Matching** feature allows investigators to quickly identify all photos containing a specific person of interest (suspect) from a large evidence collection. This powerful AI-driven tool uses advanced face recognition to automatically scan and classify photos.

---

## 🎯 How It Works

1. **Upload Suspect Photo**: Provide a clear photo of the suspect
2. **AI Analysis**: The system extracts facial features and creates a unique "face encoding"
3. **Batch Matching**: All case images are scanned and compared against the suspect
4. **Results**: Photos containing the suspect are automatically identified and sorted by confidence

---

## 📖 Step-by-Step Guide

### Step 1: Open a Case

Make sure you have a case open with imported evidence photos.

```
File → Open Case (or create a new case)
Case → Import Files (import evidence directory)
```

### Step 2: Load Suspect Photo

1. Go to **Case → 🔍 Find Suspect in Photos...** (or press `Ctrl+F`)
2. Click **"Select Suspect Photo"**
3. Choose a clear photo of the suspect
   - ✅ Photo should contain the suspect's face clearly visible
   - ✅ Good lighting and frontal/semi-frontal view works best
   - ❌ Avoid blurry, dark, or highly angled photos

### Step 3: Configure Matching Sensitivity

Adjust the tolerance slider based on your needs:

- **Strict (0.40-0.54)**: Fewer matches, higher accuracy, may miss some photos
- **Recommended (0.55-0.65)**: Balanced accuracy and recall
- **Relaxed (0.66-0.70)**: More matches, may include false positives

**💡 Tip**: Start with the default (0.60) and adjust if needed.

### Step 4: Start Matching

1. Click **"🔍 Start Face Matching"**
2. Wait for the matching process to complete
   - Progress is shown in real-time
   - You can cancel anytime
3. Review the results summary

### Step 5: View Matched Photos

After matching completes:

- **File list automatically filters** to show only suspect matches
- Photos are sorted by **confidence** (highest first)
- Each row shows:
  - ✓ Match indicator
  - Confidence percentage
  - Number of matching faces
  - Filename and metadata

### Step 6: Review Individual Photos

1. Click on any matched photo in the list
2. View the full image in the preview panel
3. Verify the match visually
4. Flag important evidence if needed

### Step 7: Reset or Re-Match

- **To see all files again**: Select "All Files" from the filter dropdown
- **To view matches again**: Select "Suspect Matches" from filter
- **To match a different suspect**: Load a new suspect photo

---

## 🔍 Understanding Results

### Confidence Levels

| Confidence | Meaning |
|------------|---------|
| 90-100% | Very high certainty - Almost definitely the suspect |
| 75-89% | High certainty - Very likely the suspect |
| 60-74% | Medium certainty - Probably the suspect |
| 50-59% | Low certainty - Possibly the suspect (verify manually) |
| <50% | Very low certainty - May be false positive |

### Match Indicators

- **✓**: Face match found
- **🎯 SUSPECT MATCH**: Status indicator
- **Green text**: Highlighting matched files
- **Multiple faces**: If a photo contains multiple people, all matching faces are counted

---

## 💡 Best Practices

### For Best Results:

1. **Use high-quality suspect photos**
   - Clear, well-lit
   - Face clearly visible
   - Minimal obstructions (sunglasses, masks, etc.)

2. **Start with recommended tolerance**
   - Don't set it too strict initially
   - You can always re-run with different settings

3. **Manually verify matches**
   - AI is powerful but not perfect
   - Always visually confirm important matches

4. **Use multiple suspect photos if available**
   - Run matching with different photos of the same suspect
   - Combine results for better coverage

### Common Issues:

**Problem**: No matches found
- **Solution**: Try a different suspect photo or increase tolerance

**Problem**: Too many false positives
- **Solution**: Decrease tolerance (make it more strict)

**Problem**: Missing known photos
- **Solution**: Increase tolerance or try a clearer suspect photo

---

## ⚙️ Technical Details

### Face Recognition Technology

- Uses **dlib's facial recognition** algorithms
- Creates 128-dimensional face encodings
- Compares using Euclidean distance
- Tolerance threshold determines match/no-match

### Performance

- **Speed**: ~0.5-1 second per image
- **Accuracy**: 95%+ with good quality photos
- **Scalability**: Can handle thousands of photos

### Limitations

- Requires faces to be visible (not completely obscured)
- Works best with frontal or semi-frontal faces
- May struggle with extreme angles, poor lighting, or heavy disguises
- Cannot match if face is not in the photo at all

---

## 🎨 UI Elements

### Suspect Photo Dialog

- **Photo preview**: Shows the loaded suspect photo
- **Face detection**: Indicates how many faces were detected
- **Tolerance slider**: Adjust matching strictness
- **Color coding**:
  - 🟢 Green: Recommended range
  - 🟡 Yellow: Relaxed (more false positives)
  - 🔴 Red: Strict (may miss matches)

### File List (Match Mode)

- **Filter**: "Suspect Matches" filter is auto-selected
- **Sorting**: By confidence (highest first)
- **Display**: Shows confidence % and face count
- **Reset**: Click "All Files" to return to normal view

---

## 📊 Workflow Example

**Scenario**: You have 500 evidence photos and need to find all photos of a robbery suspect.

1. **Open case** with 500 imported photos
2. **Load suspect photo** (from ID card or security camera)
3. **Set tolerance** to 0.60 (recommended)
4. **Start matching** (takes ~5-10 minutes for 500 photos)
5. **Review results**: 23 matches found
6. **Inspect top matches**: Verify high-confidence matches first
7. **Flag relevant evidence**: Mark important photos
8. **Export report**: Include matched photos in case report

**Time saved**: Manual review of 500 photos could take hours. AI matching completes in minutes!

---

## 🔐 Privacy & Security

- All face matching is performed **locally** on your machine
- No data is sent to external servers
- Face encodings are **temporary** (not stored permanently)
- Suspect photos are only used for the current matching session

---

## 🆘 Troubleshooting

### "No face detected in suspect photo"
- **Cause**: Face is too small, blurry, or not visible
- **Fix**: Use a clearer, closer photo of the suspect

### "Face matching failed"
- **Cause**: Corrupt image files or insufficient memory
- **Fix**: Check image files, restart application

### "Matching is very slow"
- **Cause**: Large number of high-resolution images
- **Fix**: This is normal; be patient or run on a faster computer

### "Getting unexpected matches"
- **Cause**: Tolerance too high or similar-looking people
- **Fix**: Decrease tolerance, manually verify results

---

## 📚 Additional Resources

- **Face Recognition Library**: https://github.com/ageitgey/face_recognition
- **dlib Documentation**: http://dlib.net/
- **Best practices for forensic face recognition**: See docs/best_practices.md

---

## 🔄 Version History

### Version 1.0 (Current)
- Initial release of suspect face matching feature
- Support for single suspect photo
- Adjustable tolerance
- Batch processing with progress
- Filtered results display

### Planned Features (Future)
- Multiple suspect photos (person gallery)
- Face clustering (group similar faces automatically)
- Export annotated images with bounding boxes
- Comparison reports

---

**For support or questions, contact Forenstiq AI Technologies**

---

*This feature is designed for law enforcement and forensic investigators. Use responsibly and in accordance with applicable laws and regulations.*
