// Copyright (c) 2023 Computer Vision Center (CVC) at the Universitat Autonoma
// de Barcelona (UAB).
//
// This work is licensed under the terms of the MIT license.
// For a copy, see <https://opensource.org/licenses/MIT>.

#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "CarlaTools.h"

#include "DigitalTwinsBaseWidget.generated.h"

class UOpenDriveToMap;

UCLASS(BlueprintType)
class CARLATOOLS_API UDigitalTwinsBaseWidget : public UEditorUtilityWidget
{
  GENERATED_BODY()
public:

  UFUNCTION(BlueprintCallable)
  UOpenDriveToMap* InitializeOpenDriveToMap(TSubclassOf<UOpenDriveToMap> BaseClass);

  UFUNCTION(BlueprintPure)
  UOpenDriveToMap* GetOpenDriveToMap();

  UFUNCTION(BlueprintCallable)
  void SetOpenDriveToMap(UOpenDriveToMap* ToSet);

  UFUNCTION(BlueprintCallable)
  void DestroyOpenDriveToMap();

  UFUNCTION(BlueprintCallable, Category = "Preprocessing")
	  void SetRemovalPercentage(float NewPercentage);

  UFUNCTION(BlueprintCallable, Category = "Preprocessing")
  float GetRemovalPercentage();

  UFUNCTION(BlueprintCallable, Category = "Preprocessing")
	  void PassDigitalTwinsBaseWidgetToOpenDrive(UOpenDriveToMap* OpenDriveInstance);
  UPROPERTY(BlueprintReadWrite, Category = "Preprocessing")
	  float RemovalPercentage;

  UPROPERTY(BlueprintReadWrite, Category = "Preprocessing")
      float MinHeight;

  UPROPERTY(BlueprintReadWrite, Category = "Preprocessing")
      float MaxHeight;

  UPROPERTY(BlueprintReadWrite, Category = "Preprocessing")
      float MinLevel;

  UPROPERTY(BlueprintReadWrite, Category = "Preprocessing")
      float MaxLevel;

  UFUNCTION(BlueprintCallable)
      void SetMinHeight(float InMinHeight);

  UFUNCTION(BlueprintCallable)
      void SetMaxHeight(float InMaxHeight);

  UFUNCTION(BlueprintCallable)
      void SetMinLevel(float InMinLevel);

  UFUNCTION(BlueprintCallable)
      void SetMaxLevel(float InMaxLevel);
private:
};
