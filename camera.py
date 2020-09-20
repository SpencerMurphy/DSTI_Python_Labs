import numpy as np
import cv2
from keras.preprocessing import image
from keras.models import load_model
from keras.applications.vgg16 import preprocess_input as preprocess_input_vgg

model = load_model("weights_sigmoid.h5")
model.optimizer.lr

cap = cv2.VideoCapture(0)
nb_classes = 2
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    output = frame.copy()
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #frame = cv2.resize(frame, (224, 224)).astype("float32")

    #preds = model.predict(np.expand_dims(frame, axis=0))[0]

    #Q.append(preds)
    # Display the resulting frame

    # predicting image: getting the output vector
    #img = image.load_img(image_path, target_size=image_size)
    #img_array = image.img_to_array(img)
    img_array = cv2.resize(frame, (224, 224)) #.astype("float32")
    img_expanded = np.expand_dims(img_array, axis=0)
    preprocessed_image = preprocess_input_vgg(img_expanded)

    pred = model.predict(preprocessed_image)
    print(round(pred[0][0],2),round(pred[0][1],2))
    #classes = ["{:02d}".format(i) for i in range(1, nb_classes+1)]
    classes = ['tomate','banane']
    pred_class_idx = np.argmax(pred, axis=1)
    #print(classes)
    #classes[pred_class_idx[0]]

    text = "{}".format(classes[pred_class_idx[0]])
    #text = "fruit: {}".format(1)

    cv2.putText(output, text, (35, 50), cv2.FONT_HERSHEY_SIMPLEX,1.25, (0, 255, 0), 5)
    cv2.imshow('frame',img_array)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()