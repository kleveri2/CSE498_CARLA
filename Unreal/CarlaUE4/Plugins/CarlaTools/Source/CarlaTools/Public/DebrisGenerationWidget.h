// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de Barcelona (UAB). This work is licensed under the terms of the MIT license. For a copy, see <https://opensource.org/licenses/MIT>.

#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "DebrisGenerationWidget.generated.h"

/**
 * 
 */
UCLASS()
class CARLATOOLS_API UDebrisGenerationWidget : public UEditorUtilityWidget
{
	GENERATED_BODY()
public:
	UDebrisGenerationWidget();
	~UDebrisGenerationWidget();

	UFUNCTION(BlueprintCallable)
		void Hello();

	UFUNCTION(BlueprintCallable)
		void GenerateDebris();

	UFUNCTION(BlueprintCallable)
		void ClearDebris();
	UFUNCTION(BlueprintCallable)
		static UWorld* MyGetWorld();

};
