// pages/index/index.js
Page({
  data: {
    imageUrl: null,
    result: null,
    questions: [],
    correctCount: 0,
    totalCount: 0
  },

  // 拍照
  takePhoto() {
    const that = this;
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera'],
      success(res) {
        const tempFilePath = res.tempFiles[0].tempFilePath;
        that.setData({
          imageUrl: tempFilePath,
          questions: [],
          correctCount: 0,
          totalCount: 0
        });
        that.uploadImage(tempFilePath);
      },
      fail(err) {
        wx.showToast({
          title: '拍照失败',
          icon: 'none'
        });
      }
    });
  },

  // 从相册选择
  chooseImage() {
    const that = this;
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album'],
      success(res) {
        const tempFilePath = res.tempFiles[0].tempFilePath;
        that.setData({
          imageUrl: tempFilePath,
          questions: [],
          correctCount: 0,
          totalCount: 0
        });
        that.uploadImage(tempFilePath);
      },
      fail(err) {
        wx.showToast({
          title: '选择失败',
          icon: 'none'
        });
      }
    });
  },

  // 上传图片到后端
  uploadImage(filePath) {
    wx.showLoading({
      title: '正在识别...',
    });

    const that = this;
    wx.uploadFile({
      url: 'http://172.26.7.70:5000/detect',
      filePath: filePath,
      name: 'image',
      success(res) {
        console.log('原始返回数据:', res);
        console.log('res.data内容:', res.data);
        
        try {
          // 注意：res.data 是字符串，需要解析
          const data = JSON.parse(res.data);
          console.log('解析后的data:', data);
          
          if (data.success) {
            console.log('识别到的算式数量:', data.questions.length);
            data.questions.forEach((q, i) => {
              console.log(`算式${i+1}: ${q.num1} ${q.operator} ${q.num2} = ${q.answer} ${q.isCorrect ? '✓' : '✗'}`);
            });
            
            that.setData({
              result: {
                full_text: data.full_text,
                lines: data.lines,
                count: data.count
              },
              questions: data.questions,
              correctCount: data.questions.filter(q => q.isCorrect).length,
              totalCount: data.questions.length
            });
            
            wx.showToast({
              title: `识别到 ${data.count} 个算式`,
              icon: 'success'
            });
          } else {
            console.error('后端返回失败:', data.error);
            wx.showToast({
              title: data.error || '识别失败',
              icon: 'none'
            });
          }
        } catch (e) {
          console.error('JSON解析错误:', e);
          console.error('无法解析的字符串:', res.data);
          wx.showToast({
            title: '数据格式错误',
            icon: 'none'
          });
        }
      },
      fail(err) {
        console.error('上传失败', err);
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      },
      complete() {
        wx.hideLoading();
      }
    });
  }
});